
from grokcore import component as grok
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import interfaces
from zeam.form.base.components import loadComponents
from zope.schema import Choice
from zope.schema import interfaces as schema_interfaces
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zeam.form.base')


class ExtendingVocabulary(SimpleVocabulary):
    """A vocabulary that can be extended with terms of an another
    vocabulary on demand.
    """

    def __init__(self, terms, query=None):
        super(ExtendingVocabulary, self).__init__(terms)
        self._query = query
        self._vocabulary = None

    def addTerm(self, term):
        if term.value in self.by_value:
            raise ValueError(term)
        if term.token in self.by_token:
            raise ValueError(term)
        self.by_value[term.value] = term
        self.by_token[term.token] = term
        self._terms.append(term)

    def getVocabulary(self):
        if self._vocabulary is None and self._query is not None:
            self._vocabulary = SimpleVocabulary(list(self._query))
        return self._vocabulary

    def getTerm(self, value):
        try:
            return super(ExtendingVocabulary, self).getTerm(value)
        except LookupError:
            vocabulary = self.getVocabulary()
            if vocabulary is None:
                raise
            term = vocabulary.getTerm(value)
            self.addTerm(term)
            return term

    def getTermByToken(self, token):
        try:
            return super(ExtendingVocabulary, self).getTermByToken(token)
        except LookupError:
            vocabulary = self.getVocabulary()
            if vocabulary is None:
                raise
            term = vocabulary.getTermByToken(token)
            self.addTerm(term)
            return term


def foreign_source(value_column, info):
    """Generate a vocabulary containing terms for each possible value
    you can set in a SQLAlchemy foreign key.
    """
    defaults = []
    if not info['required']:
        defaults.append(SimpleTerm(title=_(u'(not set)'), value=None))
    session = Session()

    table = value_column.table
    columns = [value_column,]
    if 'title_column' in info:
        if isinstance(info['title_column'], basestring):
            columns.append(table.columns[info['title_column']])
        else:
            for identifier in info['title_column']:
                columns.append(table.columns[identifier])
    else:
        columns.append(value_column)
    if 'title_factory' in info:
        title_factory = info['title_factory']
    else:
        title_factory = lambda d: str(d[0])

    def create_terms(query):
        for result in query.all():
            yield SimpleTerm(
                title=title_factory(result[1:]),
                value=result[0])

    full_query = session.query(*columns)
    if 'title_query' in info:
        title_terms = create_terms(info['title_query'](full_query))
        full_terms = create_terms(full_query)
    else:
        title_terms = create_terms(full_query)
        full_terms = None

    return ExtendingVocabulary(defaults + list(title_terms), full_terms)


class ModelFieldFactory(object):
    """Generate zeam.form fields out of a SQLAlchemy model.
    """
    grok.implements(interfaces.IFieldFactory)

    def __init__(self, context):
        self.context = context

    def produce(self):
        # Be sure the components are loaded.
        loadComponents()
        table = self.context.__table__
        for column in table.columns:
            if column.primary_key:
                continue
            info = column.info.copy()
            if 'required' not in info:
                info['required'] = not column.nullable
            if 'title' not in info:
                info['title'] = unicode(column.description)
            if len(column.foreign_keys):
                # XXX There can be more than one foreign key
                foreign_key = column.foreign_keys[0]
                field = Choice(
                    __name__ = u'__dummy__',
                    title = u'__dummy__',
                    source = foreign_source(foreign_key.column, info))
            elif 'schema' in info:
                field = info['schema'](__name__ = u'__dummy__',
                                      title = u'__dummy__')
            else:
                field = schema_interfaces.IField(column.type)

            field.__name__ = str(column.name)
            field.title = info['title']
            field.required = info['required']
            field.description = info.get('description')
            if 'default' in info:
                field.default = info['default']
            result = interfaces.IField(field)
            if 'form' in info:
                for key, value in info['form'].items():
                    setattr(result, key, value)
            yield result


class ModelFields(object):
    """Object descriptor that generate and cache a list of zeam.form
    fields out of a SQLAlchemy model that it is applied on.
    """

    def __new__(cls, model=None):
        if model is not None:
            return Fields(*list(ModelFieldFactory(model).produce()))
        return object.__new__(cls, model=model)

    def __init__(self, model=None):
        self.__cache = None

    def __get__(self, form, type=None):
        if form is not None:
            model = form.context.__class__
            return Fields(*list(ModelFieldFactory(model).produce()))
        return Fields()

    def __set__(self, form, value):
        raise AttributeError



from grokcore import component as grok
from z3c.saconfig import Session
from zeam.form.base import Fields
from zeam.form.base import interfaces
from zeam.form.base.components import loadComponents
from zope.schema import Choice
from zope.schema import interfaces as schema_interfaces
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


def foreign_source(value_column, info):
    values = []
    if not info['required']:
        values.append(SimpleTerm(title='(not set)', value=None))
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

    for result in session.query(*columns).all():
        values.append(
            SimpleTerm(
                title=title_factory(result[1:]),
                value=result[0]))
    return SimpleVocabulary(values)


class ModelFieldFactory(object):
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
            result = interfaces.IField(field)
            if 'form' in info:
                for key, value in info['form'].items():
                    setattr(result, key, value)
            yield result


class ModelFields(object):

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


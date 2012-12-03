
from z3c.saconfig import Session
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


def foreign_source(value_column, options):
    """Generate a vocabulary containing terms for each possible value
    you can set in a SQLAlchemy foreign key.
    """
    defaults = []
    if not options['required']:
        defaults.append(SimpleTerm(title=_(u'(not set)'), value=None))
    session = Session()

    table = value_column.table
    columns = [value_column,]
    if 'foreignTitleColumn' in options:
        if isinstance(options['foreignTitleColumn'], basestring):
            columns.append(table.columns[options['foreignTitleColumn']])
        else:
            for identifier in options['foreignTitleColumn']:
                columns.append(table.columns[identifier])
        del options['foreignTitleColumn']
    else:
        columns.append(value_column)
    if 'foreignTitleFactory' in options:
        title_factory = options['foreignTitleFactory']
        del options['foreignTitleFactory']
    else:
        title_factory = lambda d: unicode(d[0])

    def create_terms(query):
        for result in query.all():
            yield SimpleTerm(
                title=title_factory(result[1:]),
                value=result[0])

    full_query = session.query(*columns)
    if 'foreignTitleQuery' in options:
        title_terms = create_terms(options['foreignTitleQuery'](full_query))
        full_terms = create_terms(full_query)
        del options['foreignTitleQuery']
    else:
        title_terms = create_terms(full_query)
        full_terms = None

    return ExtendingVocabulary(defaults + list(title_terms), full_terms)

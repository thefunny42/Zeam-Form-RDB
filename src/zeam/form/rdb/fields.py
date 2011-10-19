
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
    title_column = value_column
    if 'title_column' in info:
        title_column = title_column.table.columns[info['title_column']]
    for result in session.query(title_column, value_column).all():
        values.append(SimpleTerm(title=str(result[0]), value=result[1]))
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
            yield interfaces.IField(field)


class ModelFields(object):

    def __init__(self, model=None):
        self.__model = model
        self.__cache = None

    def __get__(self, form, type=None):
        model = self.__model
        if model is None:
            if form is not None:
                model = form.context.__class__
            else:
                return Fields()

        return Fields(*list(ModelFieldFactory(model).produce()))

    def __set__(self, form, value):
        raise AttributeError


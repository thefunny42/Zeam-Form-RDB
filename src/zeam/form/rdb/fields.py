

from zeam.form.base import interfaces
from zeam.form.base import Fields
from zeam.form.base.components import loadComponents
from zope.schema import interfaces as schema_interfaces
from grokcore import component as grok


class ModelFieldFactory(object):
    grok.implements(interfaces.IFieldFactory)

    def __init__(self, context):
        self.context = context

    def produce(self):
        loadComponents()
        table = self.context.__table__
        for column in table.columns:
            if len(column.foreign_keys) or column.primary_key:
                continue
            field = schema_interfaces.IField(column.type)
            field.__name__ = str(column.name)
            if column.description:
                if isinstance(column.description, str):
                    field.title = unicode(column.description)
            else:
                field.title = column.description
            field.required = not column.nullable
            yield interfaces.IField(field)


class ModelFields(object):

    def __init__(self, model=None):
        self.model = model

    def __get__(self, form, type=None):
        model = self.model
        if model is None:
            if form is not None:
                model = form.context.__class__
            else:
                return Fields()

        return Fields(*list(ModelFieldFactory(model).produce()))

    def __set__(self, form, value):
        raise AttributeError


def registerDefault():
    pass

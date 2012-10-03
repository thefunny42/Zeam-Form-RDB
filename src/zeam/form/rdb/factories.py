
import sqlalchemy
from grokcore import component as grok

from zope.component import provideAdapter
from zope.interface import Interface
from zeam.form.base.interfaces import IFieldFactory
from zeam.form.ztk import widgets as fields
from zeam.form.rdb.source import foreign_source

class IFieldBuilder(Interface):
    pass


class SQLFieldFactory(object):
    grok.implements(IFieldBuilder)
    field = fields.TextLineField
    sql_field = sqlalchemy.types.String

    def __init__(self, sql_type):
        self.sql_type = sql_type

    @classmethod
    def register(cls):
        provideAdapter(cls, (cls.sql_field,), IFieldBuilder)

    def __call__(self, sql_field):
        options = sql_field.info.copy()
        if 'identifier' not in options:
            options['identifier'] = sql_field.name
        if 'title' not in options:
            options['title'] = unicode(sql_field.description)
        if 'required' not in options:
            options['required'] = not sql_field.nullable
        if 'defaultValue' not in options:
            if sql_field.default is not None:
                options['defaultValue'] = sql_field.default.arg
        if len(sql_field.foreign_keys):
            foreign_key = sql_field.foreign_keys[0]
            factory = fields.ChoiceField
            options['source'] = foreign_source(foreign_key.column, options)
        elif 'factory' in options:
            factory = options['factory']
            del options['factory']
        else:
            factory = self.field
        return factory(**options)


class StringFieldFactory(SQLFieldFactory):
    pass


class TextFieldFactory(SQLFieldFactory):
    field = fields.TextField
    sql_field = sqlalchemy.types.Text


class IntegerFieldFactory(SQLFieldFactory):
    field = fields.IntegerField
    sql_field = sqlalchemy.types.Integer


class FloatFieldFactory(SQLFieldFactory):
    field = fields.FloatField
    sql_field = sqlalchemy.types.Float


class DateFieldFactory(SQLFieldFactory):
    field = fields.DateField
    sql_field = sqlalchemy.types.Date


class DatetimeFieldFactory(SQLFieldFactory):
    field = fields.DatetimeField
    sql_field = sqlalchemy.types.DateTime


class TimeFieldFactory(SQLFieldFactory):
    field = fields.TimeField
    sql_field = sqlalchemy.types.Time


class BooleanFieldFactory(SQLFieldFactory):
    field = fields.BooleanField
    sql_field = sqlalchemy.types.Boolean


class ColumnFieldFactory(object):
    """Generate zeam.form fields out of a SQLAlchemy column.
    """
    grok.implements(IFieldFactory)

    def __init__(self, column):
        self.column = column

    def produce(self):
        factory = IFieldBuilder(self.column.type)
        yield factory(self.column)


class TableFieldFactory(object):
    """Generate zeam.form fields out of a SQLAlchemy table.
    """
    grok.implements(IFieldFactory)

    def __init__(self, table):
        self.table = table

    def produce(self):
        for column in self.table.columns:
            if column.primary_key:
                continue
            factory = IFieldBuilder(column.type)
            yield factory(column)


def register():
    # Factories
    StringFieldFactory.register()
    TextFieldFactory.register()
    IntegerFieldFactory.register()
    FloatFieldFactory.register()
    DateFieldFactory.register()
    DatetimeFieldFactory.register()
    TimeFieldFactory.register()
    BooleanFieldFactory.register()
    # Field producer
    provideAdapter(
        ColumnFieldFactory,
        (sqlalchemy.Column,))
    provideAdapter(
        TableFieldFactory,
        (sqlalchemy.Table,))

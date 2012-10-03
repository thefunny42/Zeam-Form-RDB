

from zeam.form.base import Fields

class ModelFields(object):
    """Object descriptor that generate and cache a list of zeam.form
    fields out of a SQLAlchemy model that it is applied on.
    """

    def __new__(cls, model=None):
        if model is not None:
            return Fields(model.__table__)
        return object.__new__(cls, model=model)

    def __init__(self, model=None):
        self.__cache = None

    def __get__(self, form, type=None):
        if form is not None:
            model = form.context.__class__
            return Fields(model.__table__)
        return Fields()

    def __set__(self, form, value):
        raise AttributeError


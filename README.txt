=============
zeam.form.rdb
=============


``zeam.form.rdb`` provides an helper to generate form fields for
`zeam.form.base`_, using `zeam.form.ztk`_ fields from an `SQLAlchemy`_
model.

To accomplish, you must create your fields using the descriptor
``ModelFields`` in your form. It will automatically fetch the context
of the form, and generate the fields accordingly, caching them (for
performance reasons).

Example::

  from zeam.form.rdb import ModelFields
  from zeam.form.base import Form

  class MyForm(Form):
      label = "Test form"
      fields = ModelFields()


In your `SQLAlchemy`_ schema, you can use the extra dictionnary
``info`` to control the widget generated. Foreign key will generate a
choice of possible values to select, using the column you desire as
title.

Example::

    from sqlalchemy import Column, ForeignKey
    from sqlalchemy.types import Integer, String
    from zope import schema

    idT_Effort = Column(
        'idT_Effort',
        Integer,
        primary_key=True,
        info={'title': u"Identifier"})
    idT_Opportunity = Column(
        'idT_Opportunity',
        Integer,
        ForeignKey('T_Opportunity.idT_Opportunities'),
        info={'title': u'Opportunity',
              'title_column': 'Title'})
    Name = Column(
        'Name',
        String(45))
    URL = Column(
        'URL',
        String(63),
        info={'title': u"URL",
              'schema': schema.URI})


For a ForeignKey, you have the possibility to provides multiple
columns to ``title_column``, and a function to be called to create the
title as ``title_factory``, both in the ``info``
dictionnary. ``title_query`` can specified to refine the SQLAlchemy
request used to obtain the title terms.

A field will be required unless the column is nullable, or the option
``required`` is given through ``info``.

``title`` and ``description`` from ``info`` will be used as well in
order to create the form field.


.. _zeam.form.base: http://pypi.python.org/pypi/zeam.form.base
.. _zeam.form.ztk: http://pypi.python.org/pypi/zeam.form.ztk
.. _SQLAlchemy: http://www.sqlalchemy.org/

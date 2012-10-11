from setuptools import setup, find_packages
import os

version = '1.0'

tests_require = [
    'zope.app.wsgi',
    'zope.testing',
    'zeam.form.ztk [test]',
    ]

setup(name='zeam.form.rdb',
      version=version,
      description="Extra SQLAlchemy support for zeam.form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zeam form rdb',
      author='Sylvain Viollon',
      author_email='thefunny@gmail.com',
      url='http://pypi.python.org/pypi/zeam.form.rdb',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['zeam', 'zeam.form'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'grokcore.component',
        'setuptools',
        'sqlalchemy',
        'z3c.saconfig',
        'zeam.form.base >= 1.0',
        'zeam.form.ztk',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        ],
      entry_points="""
      # -*- Entry points: -*-
      [zeam.form.components]
      factories = zeam.form.rdb.factories:register
      """,
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )

from distutils.core import setup
import py2exe

setup(
    console = ['menu.py'],
    options = {'py2exe': {
                'packages': ['psycopg2'],
                'dll_excludes':['msvcr80']
                          }
               }
    )

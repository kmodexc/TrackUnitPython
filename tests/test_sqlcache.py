from datetime import datetime
from pytrackunit.sqlcache import SqlCache
import os
import os.path


DB_FILE = "pytest-db.sqlite"
VEH = '2552712'
START = datetime(2022,1,1,10,0,0,0)
END = datetime(2022,1,30,10,0,0,0)
API_KEY = open("api.key").read()
AUTH = ('API',API_KEY)

def test_init():
    cache = SqlCache(db_file=DB_FILE)

def test_clean():
    cache = SqlCache(db_file=DB_FILE)
    assert os.path.isfile(DB_FILE)
    cache.clean()
    assert not os.path.isfile(DB_FILE)

def test_get_errors():
    cache = SqlCache(db_file=DB_FILE)
    cache.clean()
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE)
    cache.get_errors(VEH,START,END)
    cache.clean()

def test_get_errors_twice():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE)
    cache.get_errors(VEH,START,END)
    res = cache.get_errors(VEH,START,END)
    cache.clean()

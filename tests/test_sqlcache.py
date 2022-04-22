import asyncio
import pytest
from datetime import datetime
from pytrackunit.sqlcache import *
import os
import os.path

pytest_plugins = ('pytest_asyncio',)

DB_FILE = "pytest-db.sqlite"
VEH = '2552712'
START = datetime(2022,1,1,10,0,0,0)
END = datetime(2022,1,30,10,0,0,0)
MID = datetime(2022,1,15,10,0,0,0)
API_KEY = open("api.key").read()
AUTH = ('API',API_KEY)

class CacheForTests:
    """tucache class"""
    def __init__(self):
        self.return_only_cache_files = False
        self.dont_return_data = False
        self.dont_read_files = False
        self.veh_id = []
        self.start = []
        self.end = []
        self.previter = []
        self._clean = False
        self.testobj = {}
        self.testobj["id"] = VEH
        self.testobj["time"] = MID.isoformat()
        self.testobj["spn"] = 3
        self.testobj["fmi"] = 4
        self.testobj["occurrenceCount"] = 5
        self.testobj["name"] = "6"
        self.testobj["description"] = "7"
        self.testmeta = {}
        self.testmeta["id"] = VEH
        self.modifiy_time = True
    def get_testobj(self, nr,time=None):
        self.testobj["fmi"] = 4 + nr
        if time is not None:
            self.testobj["time"] = time.isoformat()
        return self.testobj
    async def ret_val_generator(self,offset):
        print("Start generator with offset",offset)
        for i in range(10):                
            yield [self.get_testobj(i+offset)], self.testmeta
    def clean(self):
        self._clean = True
    def get_faults_timedelta(self,veh_id,start,end,previter):
        if self.modifiy_time:
            self.testobj["time"] = start.isoformat()
        self._clean = False
        print(veh_id,start,end,previter)
        self.veh_id.append(veh_id)
        self.start.append(start)
        self.end.append(end)
        self.previter.append(previter)
        return self.ret_val_generator(10*(len(self.veh_id)-1)), 10

class PseudoDB:
    class PseudoDBCursor:
        def __init__(self,throw_integrity_error=-1):
            self.exm_command = []
            self.exm_data = []
            self.throw_integrity_error=throw_integrity_error
            self.ex_command = []
            self.ex_data = []
        def execute(self,command,data):
            print("PseudodbCursor",command,data)
            self.ex_command.append(command)
            self.ex_data.append(data)
            if len(self.ex_data) == self.throw_integrity_error:
                raise sqlite3.IntegrityError("Test Integrity Error")
        def executemany(self,command,data):
            self.exm_command.append(command)
            self.exm_data.append(list(data))
            if len(self.exm_data) == self.throw_integrity_error:
                raise sqlite3.IntegrityError("Test Integrity Error")
    def __init__(self):
        self.throw_integrity_error=-1
        self.commit_cnt = 0
        self.cursors = []
        self.rollback_cnt = 0
    def commit(self):
        self.commit_cnt += 1
    def cursor(self):
        cursor = self.PseudoDBCursor(self.throw_integrity_error)
        self.cursors.append(cursor)
        return cursor
    def rollback(self):
        self.rollback_cnt += 1

def test_error_item_conversion():
    _meta = {}
    _meta['id'] = "1"

    _x = {}    
    _x['time'] = START.isoformat()
    _x['spn'] = 3
    _x['fmi'] = 4
    _x['occurrenceCount'] = 5
    _x['name'] = "testname"
    _x['description'] = "testdesc"
    
    xsql = error_item_to_sql_item(_x,_meta)

    res = sql_item_to_error_item(xsql)

    _x['id'] = _meta['id']

    assert res == _x

@pytest.mark.asyncio
async def test_sqlinsertiter():
    cache = CacheForTests()
    db = PseudoDB()
    it = SqlInsertIter(cache.ret_val_generator(0),cache.testmeta,db)
    async for x in it:
        print(x)
    assert len(db.cursors) == 1
    assert len(db.cursors[0].exm_command) == 10
    assert len(db.cursors[0].exm_data) == 10
    assert len(db.cursors[0].exm_data[0]) == 1
    assert db.cursors[0].exm_command[0] == "INSERT INTO error VALUES (?,?,?,?,?,?,?)"
    assert db.cursors[0].exm_data[-1][0] == error_item_to_sql_item(cache.testobj,cache.testmeta)

@pytest.mark.asyncio
async def test_sqlinsertiter_integrity_error():
    cache = CacheForTests()
    db = PseudoDB()
    db.throw_integrity_error=5
    it = SqlInsertIter(cache.ret_val_generator(0),cache.testmeta,db)
    cnt = 0

    with pytest.raises(sqlite3.IntegrityError) as exc:
        async for x in it:
            print(x)
            cnt += 1

    assert len(db.cursors) == 1
    assert len(db.cursors[0].exm_data) == 5
    assert len(db.cursors[0].ex_data) == 1
    assert db.rollback_cnt == 1
    assert db.commit_cnt == 0

    print("second attempt")

    db.throw_integrity_error=-1

    it = SqlInsertIter(cache.ret_val_generator(0),cache.testmeta,db)
    cnt = 0  
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.get_testobj(cnt)
        cnt += 1

    assert len(db.cursors) == 2
    assert len(db.cursors[0].exm_data) == 5
    assert len(db.cursors[0].ex_data) == 1
    assert len(db.cursors[1].exm_data) == 10
    assert len(db.cursors[1].ex_data) == 0
    assert db.rollback_cnt == 1
    assert db.commit_cnt == 1
    
def test_init():
    cache = SqlCache(db_file=DB_FILE)

def test_clean():
    cache = SqlCache(db_file=DB_FILE)
    assert os.path.isfile(DB_FILE)
    cache.clean()
    assert not os.path.isfile(DB_FILE)

def test_get_faults_timedelta():
    cache = SqlCache(db_file=DB_FILE)
    cache.clean()
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE)
    cache.get_faults_timedelta(VEH,START,END)
    cache.clean()

def test_get_faults_twice():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE)
    cache.get_faults_timedelta(VEH,START,END)
    res = cache.get_faults_timedelta(VEH,START,END)
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_same_block():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    assert len(cache.cache.veh_id) == 1
    assert len(cache.cache.start) == 1
    assert len(cache.cache.end) == 1
    assert len(cache.cache.previter) == 1
    for x in cache.cache.veh_id:
        assert x == VEH
    for x in cache.cache.start:
        assert x == START
    for x in cache.cache.end:
        assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_smaller_block():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    cache.cache.modifiy_time = False
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START+timedelta(days=10),END-timedelta(days=10))
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    assert len(cache.cache.veh_id) == 1
    assert len(cache.cache.start) == 1
    assert len(cache.cache.end) == 1
    assert len(cache.cache.previter) == 1
    for x in cache.cache.veh_id:
        assert x == VEH
    for x in cache.cache.start:
        assert x == START
    for x in cache.cache.end:
        assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_bigger_block():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START-timedelta(days=10),END+timedelta(days=10))
    assert len(it.iterators) == 3
    cnt = 0
    async for x,meta in it.iterators[0]:
        assert len(x) == 1
        print(cnt)
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print(it.iterators[1])
    async for x,meta in it.iterators[1]:
        assert len(x) == 1
        print(cnt)
        assert x[0] == cache.cache.get_testobj(cnt-10,time=START)
        cnt += 1
    assert cnt == 20
    async for x,meta in it.iterators[2]:
        assert len(x) == 1
        print(cnt)
        assert x[0] == cache.cache.get_testobj(cnt-10)
        cnt += 1
    assert cnt == 30
    assert len(cache.cache.veh_id) == 3
    assert len(cache.cache.start) == 3
    assert len(cache.cache.end) == 3
    assert len(cache.cache.previter) == 3
    for x in cache.cache.veh_id:
        assert x == VEH
    # for x in cache.cache.start:
    #     assert x == START
    # for x in cache.cache.end:
    #     assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_part_bigger_block_1():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START-timedelta(days=10),END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        cnt += 1
    assert cnt == 20
    assert len(cache.cache.veh_id) == 2
    assert len(cache.cache.start) == 2
    assert len(cache.cache.end) == 2
    assert len(cache.cache.previter) == 2
    for x in cache.cache.veh_id:
        assert x == VEH
    # for x in cache.cache.start:
    #     assert x == START
    # for x in cache.cache.end:
    #     assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_part_bigger_block_2():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START,END+timedelta(days=10))
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        cnt += 1
    assert cnt == 20
    assert len(cache.cache.veh_id) == 2
    assert len(cache.cache.start) == 2
    assert len(cache.cache.end) == 2
    assert len(cache.cache.previter) == 2
    for x in cache.cache.veh_id:
        assert x == VEH
    # for x in cache.cache.start:
    #     assert x == START
    # for x in cache.cache.end:
    #     assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_overlapping_1():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START-timedelta(days=10),END-timedelta(days=10))
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        cnt += 1
    assert cnt == 20
    assert len(cache.cache.veh_id) == 2
    assert len(cache.cache.start) == 2
    assert len(cache.cache.end) == 2
    assert len(cache.cache.previter) == 2
    for x in cache.cache.veh_id:
        assert x == VEH
    # for x in cache.cache.start:
    #     assert x == START
    # for x in cache.cache.end:
    #     assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_with_mock_overlapping_2():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    it, cnt = cache.get_faults_timedelta(VEH,START,END)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults_timedelta(VEH,START+timedelta(days=10),END+timedelta(days=10))
    async for x,meta in it:
        assert len(x) == 1
        cnt += 1
    assert cnt == 20
    assert len(cache.cache.veh_id) == 2
    assert len(cache.cache.start) == 2
    assert len(cache.cache.end) == 2
    assert len(cache.cache.previter) == 2
    for x in cache.cache.veh_id:
        assert x == VEH
    # for x in cache.cache.start:
    #     assert x == START
    # for x in cache.cache.end:
    #     assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_get_faults_tdelta_timedelta():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    cache.tdelta_end = END
    it, cnt = cache.get_faults(VEH,END-START)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults(VEH,END-START)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    assert len(cache.cache.veh_id) == 1
    assert len(cache.cache.start) == 1
    assert len(cache.cache.end) == 1
    assert len(cache.cache.previter) == 1
    for x in cache.cache.veh_id:
        assert x == VEH
    for x in cache.cache.start:
        pass
        #assert x == START
    for x in cache.cache.end:
        pass
        #assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

@pytest.mark.asyncio
async def test_get_faults_tdelta_int_days():
    cache = SqlCache(AUTH,_dir=None,db_file=DB_FILE,upstream_cache=CacheForTests())
    cache.tdelta_end = END
    it, cnt = cache.get_faults(VEH,30)
    cnt = 0
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt)
        cnt += 1
    assert cnt == 10
    print("second get")
    it, cnt = cache.get_faults(VEH,30)
    async for x,meta in it:
        assert len(x) == 1
        assert x[0] == cache.cache.get_testobj(cnt-10)
        cnt += 1
    assert cnt == 20
    assert len(cache.cache.veh_id) == 1
    assert len(cache.cache.start) == 1
    assert len(cache.cache.end) == 1
    assert len(cache.cache.previter) == 1
    for x in cache.cache.veh_id:
        assert x == VEH
    # for x in cache.cache.start:
    #     assert x == START
    # for x in cache.cache.end:
    #     assert x == END
    for x in cache.cache.previter:
        assert x == None
    cache.clean()

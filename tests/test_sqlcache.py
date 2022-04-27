from copy import deepcopy
from tabnanny import verbose
import pytest
from datetime import datetime, timedelta
from pytrackunit.sqlcache import *
import os
import os.path
import json
from dateutil.parser import isoparse
import sqlite3
from pytrackunit.helper import SecureString

pytest_plugins = ('pytest_asyncio',)

# ---------------- setup ---------------------

db_path = "pytest-db.sqlite"
VEH = '2552712'
START = datetime(2022,1,1,10,0,0,1000)
END = datetime(2022,1,30,10,0,0,1000)
MID = datetime(2022,1,15,10,0,0,1000)
#API_KEY = open("api.key").read()
API_KEY = "asdfasdfasdfasdfasdfasdfasdfasdf"
AUTH = (SecureString('API'),SecureString(API_KEY))

EXAMPLE_HIST_OBJ = json.loads("""{
                    "accessKey": "",
                    "time": "2014-09-01T12:00:25.010000",
                    "latitude": 56.025915,
                    "longitude": 12.590625,
                    "streetAddress": "Haderslevvej 18",
                    "postalCode": "3000",
                    "city": "Helsingør",
                    "country": "DK",
                    "heading": 238,
                    "speed": 0,
                    "km": 80353,
                    "run1": 0,
                    "run2": 7314600,
                    "runOdo": 5609160,
                    "input1": false,
                    "input2": true,
                    "output3": false,
                    "battery": 4158,
                    "batteryPercentage": 95,
                    "externalPower": 13905
                }""")

EXAMPLE_CANDATA_OBJ = json.loads("""{
            "time": "2015-11-11T05:32:09.0000000Z",
            "variableId": 225,
            "name": "Hydraulic SW ID (1)",
            "value": "RC3-02D"
        }""")

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
        self.testmeta["start_ts"] = START.timestamp()
        self.testmeta["end_ts"] = END.timestamp()
        self.testmeta["start_ts_ms"] = self.testmeta["start_ts"] * 1000
        self.testmeta["end_ts_ms"] = self.testmeta["end_ts"] * 1000
        self.modifiy_time = True
    def get_testobj(self, nr,time=None):
        obj = deepcopy(self.testobj)
        obj["fmi"] = 4 + nr
        if time is not None:
            obj["time"] = (time+timedelta(milliseconds=nr)).isoformat()
        else:
            obj['time'] = (isoparse(obj['time'])+timedelta(milliseconds=nr)).isoformat()
        return obj
    async def ret_val_generator(self,offset,starttime):
        print("Start generator with offset",offset)
        for i in range(10):                
            yield [self.get_testobj(i+offset,starttime)], self.testmeta
    def get_hist_obj(self, nr,time=None):
        obj = deepcopy(EXAMPLE_HIST_OBJ)
        if time is not None:
            obj["time"] = (time+timedelta(milliseconds=nr)).isoformat()
        else:
            obj['time'] = (isoparse(obj['time'])+timedelta(milliseconds=nr)).isoformat()
        return obj
    async def ret_hist_generator(self,offset,starttime):
        print("Start generator with offset",offset)
        for i in range(10):                
            yield [self.get_hist_obj(i+offset,starttime)], self.testmeta
    def get_candata_obj(self, nr,time=None):
        obj = deepcopy(EXAMPLE_CANDATA_OBJ)
        if time is not None:
            obj["time"] = (time+timedelta(milliseconds=nr)).isoformat()
        else:
            obj['time'] = (isoparse(obj['time'])+timedelta(milliseconds=nr)).isoformat()
        return obj
    async def ret_candata_generator(self,offset,starttime):
        print("Start generator with offset",offset)
        for i in range(10):                
            yield [self.get_candata_obj(i+offset,starttime)], self.testmeta
    def clean(self):
        self._clean = True
    def get_faults_timedelta(self,veh_id,start,end,previter):
        if self.modifiy_time:
            _start = start
        else:
            _start = None
        self._clean = False
        print(veh_id,start,end,previter)
        self.veh_id.append(veh_id)
        self.start.append(start)
        self.end.append(end)
        self.previter.append(previter)
        return self.ret_val_generator(10*(len(self.veh_id)-1),_start), 10
    def get_history_timedelta(self,veh_id,start,end,previter):
        if self.modifiy_time:
            _start = start
        else:
            _start = None
        self._clean = False
        print(veh_id,start,end,previter)
        self.veh_id.append(veh_id)
        self.start.append(start)
        self.end.append(end)
        self.previter.append(previter)
        return self.ret_hist_generator(10*(len(self.veh_id)-1),_start), 10
    def get_candata_timedelta(self,veh_id,start,end,previter):
        if self.modifiy_time:
            _start = start
        else:
            _start = None
        self._clean = False
        print(veh_id,start,end,previter)
        self.veh_id.append(veh_id)
        self.start.append(start)
        self.end.append(end)
        self.previter.append(previter)
        return self.ret_candata_generator(10*(len(self.veh_id)-1),_start), 10

def dict_equal(x,y):
    for k in x:
        if not x[k] == "none" and k in y: 
            if not x[k] == y[k]:
                return False
    for k in y:
        if not y[k] == "none" and k in x: 
            if not x[k] == y[k]:
                return False
    return True

# ---------------- create_tables ---------------------

def test_create_table():
    if os.path.isfile(db_path):
        os.remove(db_path)
    create_tables(db_path)
    os.remove(db_path)
    create_tables(db_path)
    os.remove(db_path)

# ---------------- candata_item_to_sql_item ---------------------

def test_candata_item_conversion():
    _meta = {}
    _meta['id'] = "1"

    _x = {}    
    _x['time'] = START.isoformat()
    _x['variableId'] = 1
    _x['name'] = "testname"
    _x['value'] = "123.23"
    _x['uoM'] = "test unit"
    
    xsql = candata_item_to_sql_item(_x,_meta)

    res = sql_item_to_candata_item(xsql)

    _x['id'] = _meta['id']

    assert res == _x

# ---------------- sql_item_to_candata_item ---------------------

# ---------------- error_item_to_sql_item ---------------------

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

# ---------------- sql_item_to_error_item ---------------------

# ---------------- history_item_to_sql_item ---------------------

def test_history_item_conversion():
    _meta = {}
    _meta['id'] = "1"

    _x = json.loads("""{
                    "accessKey": "",
                    "time": "2014-09-01T12:00:25.010000",
                    "latitude": 56.025915,
                    "longitude": 12.590625,
                    "streetAddress": "Haderslevvej 18",
                    "postalCode": "3000",
                    "city": "Helsingør",
                    "country": "DK",
                    "heading": 238,
                    "speed": 0,
                    "km": 80353,
                    "run1": 0,
                    "run2": 7314600,
                    "runOdo": 5609160,
                    "input1": false,
                    "input2": true,
                    "output3": false,
                    "battery": 4158,
                    "batteryPercentage": 95,
                    "externalPower": 13905
                }""")

    print(_x['time'])
    _date = _x['time']
    _date = isoparse(_date)
    print(_date)
    _date = _date.timestamp()
    print(_date)
    _date = datetime.fromtimestamp(_date)
    print(_date)
    _date = _date.isoformat()
    print(_date)
    
    xsql = history_item_to_sql_item(_x,_meta)

    res = sql_item_to_history_item(xsql)

    _x['id'] = _meta['id']

    for k in res:
        if not res[k] == "none" and k in _x: 
            assert res[k] == _x[k]

# ---------------- sql_item_to_history_item ---------------------

# ---------------- SqlInsertIter ---------------------

@pytest.mark.asyncio
async def test_sqlinsertiter():
    if os.path.isfile(db_path):
        os.remove(db_path)

    cache = CacheForTests()
    create_tables(db_path)
    it = SqlInsertIter(
        db_path=db_path,
        sqliter=cache.ret_val_generator(0,MID),
        verbose=True,
        table="error",
        timeout=1,
        **cache.testmeta)
    async for x in it:
        print(x)

    with sqlite3.connect(db_path) as db:
        with db:
            cur = db.execute("select count(*) from error")
            assert 10 == cur.fetchone()[0]

@pytest.mark.asyncio
async def test_sqlinsertiter_isloaded():
    if os.path.isfile(db_path):
        os.remove(db_path)

    cache = CacheForTests()
    create_tables(db_path)
    it = SqlInsertIter(
        db_path=db_path,
        sqliter=cache.ret_val_generator(0,MID),
        verbose=True,
        table="error",
        timeout=1,
        **cache.testmeta)
    async for x in it:
        print(x)

    with sqlite3.connect(db_path) as db:
        with db:
            cur = db.execute("select count(*) from error")
            assert 10 == cur.fetchone()[0]
            cur = db.execute("select count(*) from errormeta")
            assert 1 == cur.fetchone()[0]
            cur = db.execute("select isloaded from errormeta")
            assert True == cur.fetchone()[0]
    
@pytest.mark.asyncio
async def test_sqlinsertiter_integrity_error():
    if os.path.isfile(db_path):
        os.remove(db_path)

    db = sqlite3.connect(db_path)

    cache = CacheForTests()
    create_tables(db_path)
    it = SqlInsertIter(
        db_path=db_path,
        sqliter=cache.ret_val_generator(0,MID),
        verbose=True,
        table="error",
        timeout=1,
        **cache.testmeta)
    async for x in it:
        print(x)

    with pytest.raises(sqlite3.IntegrityError) as exc:
        it = SqlInsertIter(
            db_path=db_path,
            sqliter=cache.ret_val_generator(0,MID),
            verbose=True,
            table="error",
            timeout=1,
            **cache.testmeta)
        async for x in it:
            print(x)

    db.execute("delete from error")
    db.execute("delete from errormeta")
    db.commit()

    cur = db.execute("select count(*) from error")
    assert 0 == cur.fetchone()[0]
    
    it = SqlInsertIter(
        db_path=db_path,
        sqliter=cache.ret_val_generator(0,MID),
        verbose=True,
        table="error",
        timeout=1,
        **cache.testmeta)
    async for x in it:
        print(x)

    cur = db.cursor()
    cur = db.execute("select count(*) from error")
    cnt = cur.fetchone()[0]
    assert 10 == cnt
    db.close()

# ---------------- SqlCache init ---------------------
    
def test_init():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path) as cache:
        pass
    os.remove(db_path)

# ---------------- SqlCache reset ---------------------

def test_reset():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path) as cache: 
        assert os.path.isfile(db_path)
        cache.reset(True)
        assert os.path.isfile(db_path)
    os.remove(db_path)
    assert not os.path.isfile(db_path)

# ---------------- SqlCache get_general_upstream ---------------------

# ---------------- SqlCache get_general_sql ---------------------

# ---------------- SqlCache get_general_unixts ---------------------

# ---------------- SqlCache get_faults_timedelta ---------------------

def test_get_faults_timedelta():
    if os.path.isfile(db_path):
        os.remove(db_path)
    
    with SqlCache(auth=AUTH,_dir=None,db_path=db_path) as cache:
        cache.get_faults_timedelta(VEH,START,END)

def test_get_faults_twice():
    if os.path.isfile(db_path):
        os.remove(db_path)
    
    with SqlCache(auth=AUTH,_dir=None,db_path=db_path) as cache:
        cache.get_faults_timedelta(VEH,START,END)
        res = cache.get_faults_timedelta(VEH,START,END)

@pytest.mark.asyncio
async def test_with_mock_same_block():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        for x in cache.cache1.start:
            assert x == START
        for x in cache.cache1.end:
            assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_with_mock_smaller_block():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.cache1.modifiy_time = False
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,MID)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START+timedelta(days=10),END-timedelta(days=10))
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START+timedelta(days=14))
            cnt += 1
        assert cnt == 10
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        for x in cache.cache1.start:
            assert x == START
        for x in cache.cache1.end:
            assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_with_mock_bigger_block():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START-timedelta(days=10),END+timedelta(days=10))
        assert len(it.iterators) == 3
        cnt = 0
        async for x,meta in it.iterators[0]:
            assert len(x) == 1
            print(cnt)
            assert x[0] == cache.cache1.get_testobj(cnt+10,START-timedelta(days=10))
            cnt += 1
        assert cnt == 10
        print(it.iterators[1])
        async for x,meta in it.iterators[1]:
            assert len(x) == 1
            print(cnt)
            assert x[0] == cache.cache1.get_testobj(cnt-10,time=START)
            cnt += 1
        assert cnt == 20
        async for x,meta in it.iterators[2]:
            assert len(x) == 1
            print(cnt)
            assert x[0] == cache.cache1.get_testobj(cnt,time=END+timedelta(milliseconds=1))
            cnt += 1
        assert cnt == 30
        assert len(cache.cache1.veh_id) == 3
        assert len(cache.cache1.start) == 3
        assert len(cache.cache1.end) == 3
        assert len(cache.cache1.previter) == 3
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_with_mock_part_bigger_block_1():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START-timedelta(days=10),END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 2
        assert len(cache.cache1.start) == 2
        assert len(cache.cache1.end) == 2
        assert len(cache.cache1.previter) == 2
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_with_mock_part_bigger_block_2():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START,END+timedelta(days=10))
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 2
        assert len(cache.cache1.start) == 2
        assert len(cache.cache1.end) == 2
        assert len(cache.cache1.previter) == 2
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_with_mock_overlapping_1():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START-timedelta(days=10),END-timedelta(days=10))
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 2
        assert len(cache.cache1.start) == 2
        assert len(cache.cache1.end) == 2
        assert len(cache.cache1.previter) == 2
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_with_mock_overlapping_2():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        it, cnt = cache.get_faults_timedelta(VEH,START,END)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,START)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults_timedelta(VEH,START+timedelta(days=10),END+timedelta(days=10))
        async for x,meta in it:
            assert len(x) == 1
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 2
        assert len(cache.cache1.start) == 2
        assert len(cache.cache1.end) == 2
        assert len(cache.cache1.previter) == 2
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

# ---------------- SqlCache get_faults ---------------------

@pytest.mark.asyncio
async def test_get_faults_tdelta_timedelta():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.tdelta_end = END
        start,end = start_end_from_tdelta(END-START,END)
        it, cnt = cache.get_faults(VEH,END-START)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,start)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults(VEH,END-START)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,start)
            cnt += 1
        assert cnt == 10
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        for x in cache.cache1.start:
            pass
            #assert x == START
        for x in cache.cache1.end:
            pass
            #assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_get_faults_tdelta_int_days():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.tdelta_end = END
        start,end = start_end_from_tdelta(30,END)
        it, cnt = cache.get_faults(VEH,30)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt,start)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_faults(VEH,30)
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_testobj(cnt-10,start)
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

# ---------------- SqlCache get_history_timedelta ---------------------

# ---------------- SqlCache get_history ---------------------

@pytest.mark.asyncio
async def test_get_history_tdelta_timedelta():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.tdelta_end = END
        start,end = start_end_from_tdelta(END-START,END)
        it, cnt = cache.get_history(VEH,END-START)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_hist_obj(cnt,start)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_history(VEH,END-START)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert dict_equal(x[0],cache.cache1.get_testobj(cnt,start))
            cnt += 1
        assert cnt == 10
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        for x in cache.cache1.start:
            pass
            #assert x == START
        for x in cache.cache1.end:
            pass
            #assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_get_history_tdelta_int_days():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.tdelta_end = END
        start,end = start_end_from_tdelta(30,END)
        it, cnt = cache.get_history(VEH,30)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_hist_obj(cnt,start)
            cnt += 1
        assert cnt == 10
        print("second get")
        cnt = 0
        print(cache.cache1.get_testobj(0,start))
        print(cache.cache1.get_testobj(1,start))
        it, cnt = cache.get_history(VEH,30)
        async for x,meta in it:
            assert len(x) == 1
            # if not dict_equal(x[0],cache.cache1.get_testobj(cnt,start)):
            #     assert x[0] == cache.cache1.get_testobj(cnt,start)
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

# ---------------- SqlCache get_candata_timedelta ---------------------

# ---------------- SqlCache get_candata ---------------------

@pytest.mark.asyncio
async def test_get_candata_tdelta_timedelta():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.tdelta_end = END
        start,end = start_end_from_tdelta(END-START,END)
        it, cnt = cache.get_candata(VEH,END-START)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_candata_obj(cnt,start)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_candata(VEH,END-START)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            if not dict_equal(x[0] , cache.cache1.get_candata_obj(cnt,start)):
                assert x[0] == cache.cache1.get_candata_obj(cnt,start)
            cnt += 1
        assert cnt == 10
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        for x in cache.cache1.start:
            pass
            #assert x == START
        for x in cache.cache1.end:
            pass
            #assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_get_candata_tdelta_int_days():
    if os.path.isfile(db_path):
        os.remove(db_path)
    with SqlCache(db_path=db_path,sql_cache1=CacheForTests(),verbose=True) as cache:
        cache.tdelta_end = END
        start,end = start_end_from_tdelta(30,END)
        it, cnt = cache.get_candata(VEH,30)
        cnt = 0
        async for x,meta in it:
            assert len(x) == 1
            assert x[0] == cache.cache1.get_candata_obj(cnt,start)
            cnt += 1
        assert cnt == 10
        print("second get")
        it, cnt = cache.get_candata(VEH,30)
        async for x,meta in it:
            assert len(x) == 1
            if not dict_equal(x[0] , cache.cache1.get_candata_obj(cnt-10,start)):
                assert x[0] == cache.cache1.get_candata_obj(cnt-10,start)
            cnt += 1
        assert cnt == 20
        assert len(cache.cache1.veh_id) == 1
        assert len(cache.cache1.start) == 1
        assert len(cache.cache1.end) == 1
        assert len(cache.cache1.previter) == 1
        for x in cache.cache1.veh_id:
            assert x == VEH
        # for x in cache.cache1.start:
        #     assert x == START
        # for x in cache.cache1.end:
        #     assert x == END
        for x in cache.cache1.previter:
            assert x == None
    if os.path.isfile(db_path):
        os.remove(db_path)

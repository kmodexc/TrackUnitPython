"""Module for caching data in sql db"""

import sqlite3
import os.path
import os
from datetime import datetime
from pytrackunit.tucache import TuCache
from pytrackunit.tuiter import SqlIter, TuIter
from pytrackunit.helper import get_datetime

CREATE_HISTORY_META = '''
create table histmeta(
    unit text, 
    start text, 
    end text,
    primary key(unit, start)
)
'''

CREATE_HISTORY_TABLE = '''
CREATE TABLE history(
    unit text not null, 
    time int not null, 
    event int, 
    keyId text, 
    location text, 
    address text, 
    heading int, 
    speed real,
    km real, 
    run1 real,
    run2 real,
    run3 real,
    run4 real,
    runOdo real,
    temperature1 real,
    temperature2 real,
    input1 int,
    input2 int,
    input3 int,
    input4 int,
    input5 int,
    input6 int,
    input7 int,
    input8 int,
    input9 int,
    input10 int,
    output1 int,
    output2 int,
    output3 int,
    output4 int,
    output5 int,
    analogInput1 real,
    analogInput2 real,
    analogInput4 real,
    Input1ChangeCounter INT,
    Input2ChangeCounter INT,
    Input3ChangeCounter INT,
    Input4ChangeCounter INT,
    batteryLevel real,
    externalPower real,
    primary key (unit,time)
)
'''

CREATE_ERROR_META_TABLE = '''
CREATE TABLE errormeta(
    unit text, 
    start int, 
    end int,
    primary key(unit, start)
)
'''

CREATE_ERROR_DATA_TABLE = '''
CREATE TABLE error(
    unit text not null, 
    time int not null, 
    spn int not null,
    fmi int not null,
    occurenceCount int,
    name text,
    description text,
    primary key(unit,time,spn,fmi)
)
'''

class SqlInsertIter:
    """iterator for tucache data"""
    def __init__(self, sqliter, meta=None, _db=None):
        print("SqlInsertIter __init__ has sqliter:",sqliter)
        self.sqliter = sqliter
        self.iter_started = False
        self.meta = meta
        self._db = _db
        if self._db is not None:
            self.cur = self._db.cursor()

    def __aiter__(self):
        if self.iter_started:
            raise Exception("cant start tuiter more than once")
        self.iter_started = True
        return self

    async def __anext__(self):
        def map_f(_x,meta):
            _id = meta['id']
            #print(x['time'])
            _time = int(get_datetime(_x['time']).timestamp()*1000)
            #print(_time,x['time'],get_datetime(x['time']))
            _spn = _x['spn']
            _fmi = _x['fmi']
            _oc = _x['occurrenceCount']
            if 'name' in _x:
                _name = _x['name']
            else:
                _name = 'none'
            if 'description' in _x:
                _desc = _x['description']
            else:
                _desc = 'none'
            return (_id,_time,_spn,_fmi,_oc,_name,_desc)

        try:
            data, meta = await self.sqliter.__anext__()
            if self._db is not None:
                #print(data)
                sqldata = map(lambda x: map_f(x,meta),data)
                self.cur.executemany("INSERT INTO error VALUES (?,?,?,?,?,?,?)",sqldata)
            return data, meta
        except StopAsyncIteration as exc:
            print("Committed")
            self._db.commit()
            raise StopAsyncIteration from exc
        except StopIteration as exc:
            print("Committed")
            self._db.commit()
            raise StopAsyncIteration from exc

class SqlCache:
    """Sql cache can cache trackunit data in Sqlite DB"""
    def __init__(self,auth=None,_dir=None,db_file="webdb.db",upstream_cache=None):
        create_tables = not os.path.isfile(db_file)
        self.web_db_path = db_file
        self._db = sqlite3.connect(self.web_db_path)
        self.cache = upstream_cache
        if self.cache is None:
            self.cache = TuCache(auth,_dir,verbose=True)
        if create_tables:
            cur = self._db.cursor()
            cur.execute(CREATE_HISTORY_TABLE)
            cur.execute(CREATE_HISTORY_META)
            cur.execute(CREATE_ERROR_META_TABLE)
            cur.execute(CREATE_ERROR_DATA_TABLE)
            self._db.commit()
    def clean(self):
        """removes database file"""
        if self._db is not None:
            self._db.close()
            os.remove(self.web_db_path)
            self._db = None
    def get_history(self, unit, start):
        """returns history data of a vehicle with start and end date"""
        cur = self._db.cursor()
        try:
            meta = next(cur.execute(\
                "select * from histmeta where unit = ? and start <= ? order by start",\
                unit,start))
            print(meta)
        except StopIteration:
            print("no element found")

    def get_candata(self,unit,start):
        """returns history data of a vehicle with start and end date"""
        #tbd
    def get_errors_upstream(self, veh_id, start_ts, end_ts, previter=None):
        """gets errors from upstream cache"""
        cur = self._db.cursor()

        cur.execute("INSERT INTO errormeta VALUES (?,?,?)",(veh_id,start_ts,end_ts))
        self._db.commit()

        start = datetime.fromtimestamp(start_ts/1000.0)
        end = datetime.fromtimestamp(end_ts/1000.0)

        int_data_iter, _len = self.cache.get_faults_timedelta(veh_id,start,end,None)

        meta = {}
        meta["id"] = veh_id
        meta["start"] = start
        meta["end"] = end

        wrap_iter = SqlInsertIter(int_data_iter,meta,self._db)

        if previter is None:
            previter = TuIter()

        previter.add(wrap_iter)

        return previter, _len

    def get_errors(self, veh_id, start, end, previter=None):
        """returns error in between the given datetime objects"""
        start_ts = int(start.timestamp()*1000)
        end_ts = int(end.timestamp()*1000)
        return self.get_errors_unixts(veh_id, start_ts, end_ts, previter)

    def get_errors_unixts(self, veh_id, start_ts, end_ts, previter=None):
        """returns error in between the given datetime objects"""

        cur = self._db.cursor()

        # Query meta database to check whether there the data is in database
        try:
            _, me_start, me_end = next(iter(cur.execute("""
                select * from errormeta where unit = ? and 
                (start <= ? and end >= ?) or 
                (start <= ? and end >= ?) order by start
                """,(veh_id,start_ts,start_ts,end_ts,end_ts))))
            me_start = int(float(me_start))
            me_end = int(float(me_end))
        except StopIteration:
            print("Stop iteration. Get errors from upstream now")
            return self.get_errors_upstream(veh_id,start_ts,end_ts,previter)

        # Depending on the start and end of the next block, apply divide and conquer
        # by recursive calls of this function.
        if me_start <= start_ts:
            if me_end < end_ts:
                previter, cnt1 = self.get_errors_unixts(veh_id,start_ts,me_end,previter)
                previter, cnt2 = self.get_errors_unixts(veh_id,me_end+1,start_ts,previter)
                return previter,(cnt1+cnt2)
            return self.get_errors_sql(veh_id,start_ts,end_ts,previter)
        if me_end >= end_ts:
            previter, cnt1 = self.get_errors_unixts(veh_id,start_ts,me_start-1,previter)
            previter, cnt2 = self.get_errors_unixts(veh_id,me_start,end_ts,previter)
            return previter,(cnt1+cnt2)
        previter, cnt1 = self.get_errors_unixts(veh_id,start_ts,me_start-1,previter)
        previter, cnt2 = self.get_errors_unixts(veh_id,me_start,me_end,previter)
        previter, cnt3 = self.get_errors_unixts(veh_id,me_end+1,end_ts,previter)
        return previter,(cnt1+cnt2+cnt3)

    def get_errors_sql(self, veh_id, start_ts, end_ts, previter=None):
        """gets data of this period from db whether or not it was actually stored there"""
        cur = self._db.cursor()

        cnt = next(cur.execute(\
            """
            select count(*) from error where
            unit = ? and time >= ? and time <= ?
            order by time
            """,(veh_id,start_ts,end_ts)))[0]

        meta = {}
        meta["id"] = veh_id
        meta["start"] = start_ts
        meta["end"] = end_ts

        if previter is None:
            previter = TuIter()

        if cnt > 0:
            previter.add(SqlIter(iter(cur.execute(\
                "select * from error where unit = ? and time >= ? and time <= ? order by time",\
                    (veh_id,start_ts,end_ts))),meta))

        return previter, cnt

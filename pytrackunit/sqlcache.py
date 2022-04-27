"""Module for caching data in sql db"""

from typing import Tuple
import asyncio
from copy import deepcopy
import os.path
import os
from datetime import datetime
import sqlite3
import time
import aiosqlite
from .tucache import TuCache
from .tuiter import TuIter
from .helper import get_datetime, start_end_from_tdelta


CREATE_HISTORY_META = '''
create table historymeta(
    unit text, 
    start text, 
    end text,
    isloaded bool,
    CONSTRAINT time CHECK (start < end),
    primary key(unit, start)
)
'''

CREATE_HISTORY_TABLE = '''
CREATE TABLE history(
    unit text not null, 
    time int not null, 
    event int, 
    keyId text, 
    latitude real,
    longitude real, 
    streetAddress text,
    postalCode text,
    city text,
    country text,
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
    isloaded bool,
    CONSTRAINT time CHECK (start < end),
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

CREATE_CANDATA_META_TABLE = '''
CREATE TABLE candatameta(
    unit text, 
    start int, 
    end int,
    isloaded bool,
    CONSTRAINT time CHECK (start < end),
    primary key(unit, start)
)
'''

CREATE_CANDATA_DATA_TABLE = '''
CREATE TABLE candata(
    unit text not null, 
    time int not null, 
    variableId int not null,
    name text not null,
    value text not null,
    uoM text,
    primary key(unit,time,variableId)
)
'''

def create_tables(db_path : str) -> None:
    """Creates the necessary tables in an sqlite database which is located at db_path"""
    _db = sqlite3.connect(db_path)
    cur = _db.cursor()
    cur.execute(CREATE_HISTORY_TABLE)
    cur.execute(CREATE_HISTORY_META)
    cur.execute(CREATE_ERROR_META_TABLE)
    cur.execute(CREATE_ERROR_DATA_TABLE)
    cur.execute(CREATE_CANDATA_META_TABLE)
    cur.execute(CREATE_CANDATA_DATA_TABLE)
    _db.commit()
    _db.close()

def candata_item_to_sql_item(_x : dict,meta : dict) -> Tuple:
    """
    returns the candata as a tuple and converts the time to unix timestamp (milliseconds)
    """
    _id = meta['id']
    _time = int(get_datetime(_x['time']).timestamp()*1000)
    _variableid = _x['variableId']
    _name = _x['name']
    _value = _x['value']
    if 'uoM' in _x:
        _uom = _x['uoM']
    else:
        _uom = None
    return (_id,_time,_variableid,_name,_value,_uom)

def sql_item_to_candata_item(obj : Tuple) -> dict:
    """
    the operation candata_item_to_sql_item reversed
    """
    _x = {}
    _x['id'] = obj[0]
    _x['time'] = datetime.fromtimestamp(obj[1]/1000.0).isoformat()
    _x['variableId'] = obj[2]
    _x['name'] = obj[3]
    _x['value'] = obj[4]
    _x['uoM'] = obj[5]
    return _x

def error_item_to_sql_item(_x : dict,meta : dict) -> Tuple:
    """
    returns the error as a tuple and converts the time to unix timestamp (milliseconds)
    """
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
        _name = None
    if 'description' in _x:
        _desc = _x['description']
    else:
        _desc = None
    return (_id,_time,_spn,_fmi,_oc,_name,_desc)

def sql_item_to_error_item(obj : Tuple) -> dict:
    """
    the operation error_item_to_sql_item reversed
    """
    _x = {}
    _x['id'] = obj[0]
    _x['time'] = datetime.fromtimestamp(obj[1]/1000.0).isoformat()
    _x['spn'] = obj[2]
    _x['fmi'] = obj[3]
    _x['occurrenceCount'] = obj[4]
    _x['name'] = obj[5]
    _x['description'] = obj[6]
    return _x

# pylint: disable=invalid-name, too-many-locals
def history_item_to_sql_item(_x : dict, meta : dict) -> Tuple:
    """
    returns the history as a tuple and converts the time to unix timestamp (milliseconds)
    """
    _time = int(get_datetime(_x['time']).timestamp()*1000)
    _unit = meta['id']
    _event = _x['event'] if 'event' in _x else None
    _keyId = _x['keyId'] if 'keyId' in _x else None
    _latitude = _x['latitude'] if 'latitude' in _x else None
    _longitude = _x['longitude'] if 'longitude' in _x else None
    _streetAddress = _x['streetAddress'] if 'streetAddress' in _x else None
    _postalCode = _x['postalCode'] if 'postalCode' in _x else None
    _city = _x['city'] if 'city' in _x else None
    _country = _x['country'] if 'country' in _x else None
    _heading = _x['heading'] if 'heading' in _x else None
    _speed = _x['speed'] if 'speed' in _x else None
    _km = _x['km'] if 'km' in _x else None
    _run1 = _x['run1'] if 'run1' in _x else None
    _run2 = _x['run2'] if 'run2' in _x else None
    _run3 = _x['run3'] if 'run3' in _x else None
    _run4 = _x['run4'] if 'run4' in _x else None
    _runOdo = _x['runOdo'] if 'runOdo' in _x else None
    _temperature1 = _x['temperature1'] if 'temperature1' in _x else None
    _temperature2 = _x['temperature2'] if 'temperature2' in _x else None
    _input1 = _x['input1'] if 'input1' in _x else None
    _input2 = _x['input2'] if 'input2' in _x else None
    _input3 = _x['input3'] if 'input3' in _x else None
    _input4 = _x['input4'] if 'input4' in _x else None
    _input5 = _x['input5'] if 'input5' in _x else None
    _input6 = _x['input6'] if 'input6' in _x else None
    _input7 = _x['input7'] if 'input7' in _x else None
    _input8 = _x['input8'] if 'input8' in _x else None
    _input9 = _x['input9'] if 'input9' in _x else None
    _input10 = _x['input10']  if 'input10' in _x else None
    _output1 = _x['output1'] if 'output1' in _x else None
    _output2 = _x['output2'] if 'output2' in _x else None
    _output3 = _x['output3'] if 'output3' in _x else None
    _output4 = _x['output4'] if 'output4' in _x else None
    _output5 = _x['output5'] if 'output5' in _x else None
    _analogInput1 = _x['analogInput1'] if 'analogInput1' in _x else None
    _analogInput2 = _x['analogInput2'] if 'analogInput2' in _x else None
    _analogInput4 = _x['analogInput4'] if 'analogInput4' in _x else None
    _Input1ChangeCounter = _x['Input1ChangeCounter'] if 'Input1ChangeCounter' in _x else None
    _Input2ChangeCounter = _x['Input2ChangeCounter'] if 'Input2ChangeCounter' in _x else None
    _Input3ChangeCounter = _x['Input3ChangeCounter'] if 'Input3ChangeCounter' in _x else None
    _Input4ChangeCounter = _x['Input4ChangeCounter'] if 'Input4ChangeCounter' in _x else None
    _batteryLevel = _x['batteryLevel'] if 'batteryLevel' in _x else None
    _externalPower = _x['externalPower'] if 'externalPower' in _x else None

    return (_unit, _time, _event, _keyId, _latitude, _longitude,
        _streetAddress, _postalCode, _city, _country, _heading,
        _speed, _km, _run1, _run2, _run3, _run4, _runOdo, _temperature1,
        _temperature2, _input1, _input2, _input3, _input4, _input5,
        _input6, _input7, _input8, _input9, _input10, _output1, _output2,
        _output3, _output4, _output5, _analogInput1, _analogInput2,
        _analogInput4, _Input1ChangeCounter, _Input2ChangeCounter,
        _Input3ChangeCounter, _Input4ChangeCounter,
        _batteryLevel, _externalPower)
# pylinte: enable=invalid-name, too-many-locals

def sql_item_to_history_item(obj : Tuple) -> dict:
    """
    the operation history_item_to_sql_item reversed
    """
    _x = {}
    _x['unit'] = obj[0]
    _x['time'] = datetime.fromtimestamp(obj[1]/1000.0).isoformat()
    _x['event'] = obj[2]
    _x['keyId'] = obj[3]
    _x['latitude'] = obj[4]
    _x['longitude'] = obj[5]
    _x['streetAddress'] = obj[6]
    _x['postalCode'] = obj[7]
    _x['city'] = obj[8]
    _x['country'] = obj[9]
    _x['heading'] = obj[10]
    _x['speed'] = obj[11]
    _x['km'] = obj[12]
    _x['run1'] = obj[13]
    _x['run2'] = obj[14]
    _x['run3'] = obj[15]
    _x['run4'] = obj[16]
    _x['runOdo'] = obj[17]
    _x['temperature1'] = obj[18]
    _x['temperature2'] = obj[19]
    _x['input1'] = obj[20]
    _x['input2'] = obj[21]
    _x['input3'] = obj[22]
    _x['input4'] = obj[23]
    _x['input5'] = obj[24]
    _x['input6'] = obj[25]
    _x['input7'] = obj[26]
    _x['input8'] = obj[27]
    _x['input9'] = obj[28]
    _x['input10'] = obj[29]
    _x['output1'] = obj[30]
    _x['output2'] = obj[31]
    _x['output3'] = obj[32]
    _x['output4'] = obj[33]
    _x['output5'] = obj[34]
    _x['analogInput1'] = obj[35]
    _x['analogInput2'] = obj[36]
    _x['analogInput4'] = obj[37]
    _x['Input1ChangeCounter'] = obj[38]
    _x['Input2ChangeCounter'] = obj[39]
    _x['Input3ChangeCounter'] = obj[40]
    _x['Input4ChangeCounter'] = obj[41]
    _x['batteryLevel'] = obj[42]
    _x['externalPower'] = obj[43]
    return _x

async def SqlInsertIter(
        sqliter : TuIter,
        start_ts_ms : int,
        end_ts_ms : int,
        **kwargs) -> Tuple[list,dict]:
    """Generator which inserts data from an upstream iterator into the database"""

    db_path = kwargs['db_path']
    verbose = kwargs['verbose']
    timeout = kwargs['timeout']
    table = kwargs['table']
    veh_id = kwargs['id']

    assert db_path is not None
    assert db_path != ""

    async with aiosqlite.connect(db_path,timeout=timeout) as _db:

        if verbose:
            print("SqlInsertIter __init__ has sqliter:",sqliter)
        if table == "error":
            insert_sql = "INSERT INTO error VALUES (?,?,?,?,?,?,?)"
            fconv = error_item_to_sql_item
        elif table == "history":
            insert_sql = """
            INSERT INTO history VALUES 
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """
            fconv = history_item_to_sql_item
        elif table == "candata":
            insert_sql = """
            INSERT INTO candata VALUES 
            (?,?,?,?,?,?)
            """
            fconv = candata_item_to_sql_item
        else:
            raise Exception("Not yet implemented")

        await _db.execute(f"INSERT INTO {table}meta VALUES (?,?,?,?)",\
            (veh_id,start_ts_ms,end_ts_ms,False),)

        await _db.commit()

        async for data,meta in sqliter:
            data = list(data)
            sqldata = map(lambda x: fconv(x[0],x[1]),zip(data,[meta]))

            try:
                await _db.executemany(insert_sql,sqldata)
                await _db.commit()
            except sqlite3.IntegrityError as exc1:
                if verbose:
                    print("Integrety error with",kwargs)
                    print("Try to find double entry (insert side)")
                    for in_item in sqldata:
                        try:
                            await _db.execute(insert_sql,in_item)
                        except sqlite3.IntegrityError:
                            print("Item throwing Integrity error",in_item)
                await _db.rollback()
                raise sqlite3.IntegrityError from exc1

            yield data, meta

        await _db.execute(f"""
            UPDATE {table}meta SET isloaded=? WHERE unit=? AND start=? AND end=?
            """,(True,veh_id,start_ts_ms,end_ts_ms))

        await _db.commit()

        if verbose:
            print("Loaded",start_ts_ms,end_ts_ms,kwargs)

async def SqlReturnIter(
        start_ts_ms : int,
        end_ts_ms : int,
        **kwargs) -> Tuple[list, dict]:
    """Generator return given data from database"""

    db_path = kwargs['db_path']
    verbose = kwargs['verbose']
    timeout = kwargs['timeout']
    table = kwargs['table']
    veh_id = kwargs['id']

    command = f"""
        select * from {table} where unit = ? and time >= ? and time <= ? order by time
    """
    if table == "error":
        fconv = sql_item_to_error_item
    elif table == "history":
        fconv = sql_item_to_history_item
    elif table == "candata":
        fconv = sql_item_to_candata_item
    else:
        raise Exception("Table not implemented yet")
    async with aiosqlite.connect(db_path,timeout=timeout) as _db:

        # Wait until the block is fully loaded

        start_time = time.time()
        isloaded = False
        while not isloaded:
            async with _db.execute(f"""
                select * from {table}meta where unit = ? and start <= ? and end >= ?
                """,(veh_id,start_ts_ms,end_ts_ms)) as cur:
                first = await cur.fetchone()
                if verbose:
                    print(first)
                isloaded = first[3]
            if not isloaded:
                if time.time() - start_time > 1:
                    raise Exception(f"Timout waiting for block {start_ts_ms} {end_ts_ms} {kwargs}")
                await asyncio.sleep(0)

        async with _db.execute(command,(veh_id,start_ts_ms, end_ts_ms)) as _cur:
            async for x in _cur:
                yield [fconv(x)], kwargs

class SqlCache:
    """Sql cache can cache trackunit data in Sqlite DB"""
    def __init__(self,**kwargs):
        self.verbose = kwargs.get('verbose',False)
        self.db_path = kwargs.get('db_path','sqlcache.sqlite')
        self.tdelta_end = kwargs.get('tdelta_end',None)
        cache1_kwargs = deepcopy(kwargs)
        cache1_kwargs['dont_cache_data'] = kwargs.get('sql_cache1_dont_cache_data',True)
        self.cache1 = kwargs.get('sql_cache1',TuCache(**cache1_kwargs))
        self.cache2 = kwargs.get('sql_cache2',TuCache(**kwargs))
        self.db_connection = None
        self.timeout = kwargs.get('sql_timeout',30)
        self.connect()
        if kwargs.get('sql_repair_on_start',True):
            for table in ['error','history','candata']:
                self.repair(table)

    def connect(self) -> None:
        """Connects the SqlCache and sets up db_connection"""
        if self.db_connection is not None:
            raise Exception("Cant connect twice")
        no_db_present = not os.path.isfile(self.db_path)
        self.db_connection = sqlite3.connect(self.db_path,timeout=self.timeout)
        if no_db_present:
            create_tables(self.db_path)

    def close(self) -> None:
        """closes database connection"""
        if self.db_connection is None:
            return
        self.db_connection.close()
        self.db_connection = None

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        self.close()

    def reset(self,remove_data : bool=False) -> None:
        """removes database file"""
        self.close()
        if remove_data:
            os.remove(self.db_path)
        self.connect()

    def repair(self,table : str) -> None:
        """
        repairs the database after crash.
        deletes blocks with unloaded data
        """
        cur = self.db_connection.execute(f"""
            select * from {table}meta where
            isloaded = 0
            """)
        for veh_id, start_ts_ms, end_ts_ms, _ in cur:
            self.db_connection.execute(f"""
                DELETE FROM {table} WHERE
                unit=? AND time>=? AND time<=?
                """,(veh_id,start_ts_ms,end_ts_ms))
            self.db_connection.execute(f"""
                DELETE FROM {table}meta WHERE
                unit=? AND start=? AND end=?
                """,(veh_id,start_ts_ms,end_ts_ms))
            self.db_connection.commit()

    async def get_unitlist(self):
        """returns a list of vehicles"""
        return await self.cache2.get_unitlist()

    def get_general_upstream(
            self,
            start_ts_ms : int,
            end_ts_ms : int,
            previter : TuIter,
            **kwargs) -> Tuple[TuIter,int]:
        """
        gets errors from upstream cache
        """

        if kwargs['table'] == "error":
            f_get_timedelta = self.cache1.get_faults_timedelta
        elif kwargs['table'] == "history":
            f_get_timedelta = self.cache1.get_history_timedelta
        elif kwargs['table'] == "candata":
            f_get_timedelta = self.cache1.get_candata_timedelta
        else:
            raise Exception("Not Implemented")

        start = datetime.fromtimestamp(start_ts_ms/1000)
        end = datetime.fromtimestamp(end_ts_ms/1000)

        int_data_iter, _len = f_get_timedelta(kwargs['id'],start,end,None)

        wrap_iter = SqlInsertIter(
            int_data_iter,
            start_ts_ms,
            end_ts_ms,
            db_path=self.db_path,
            verbose=self.verbose,
            timeout=self.timeout,
            **kwargs)

        if previter is None:
            previter = TuIter()

        previter.add(wrap_iter)

        return previter, _len
    def get_general_sql(self,
        start_ts_ms : int,
        end_ts_ms : int,
        previter : TuIter,
        **kwargs) -> Tuple[TuIter,int]:
        """
        gets data of this period from db whether or not it was actually stored there
        start_ts_ms and end_ts_ms are unix timestamps in milliseconds so the milliseconds since 1970
        """

        cur = self.db_connection.execute(f"""
            select count(*) from {kwargs['table']} where
            unit = ? and time >= ? and time <= ?
            order by time
            """,(kwargs['id'],start_ts_ms,end_ts_ms))
        cnt = cur.fetchone()[0]

        if self.verbose:
            print("found",cnt,"in sql")

        if previter is None:
            previter = TuIter()

        if cnt > 0:
            previter.add(SqlReturnIter(
                start_ts_ms,
                end_ts_ms,
                db_path=self.db_path,
                verbose=self.verbose,
                timeout=self.timeout,
                **kwargs))
        elif self.verbose:
            print("could not find any item in block ",start_ts_ms,end_ts_ms,"for unit",kwargs['id'])

        return previter, cnt
    def get_general_unixts(self,
            start_ts_ms : int,
            end_ts_ms : int,
            previter : TuIter,
            **kwargs) -> Tuple[TuIter,int]:
        """
        returns error in between the given datetime objects
        start_ts_ms and end_ts_ms are unix timestamps in milliseconds so the milliseconds since 1970
        """

        # Query meta database to check whether there the data is in database
        cur = self.db_connection.execute(f"""
            select * from {kwargs["table"]}meta where unit = ? and (
            (start <= ? and end > ?) or 
            (start < ? and end >= ?) or
            (start >= ? and end <= ?)
            ) order by start
            """,(kwargs['id'],start_ts_ms,start_ts_ms,end_ts_ms,end_ts_ms,start_ts_ms,end_ts_ms))
        first = cur.fetchone()
        if first is not None:
            me_vehid, me_start, me_end = first[0], first[1], first[2]
        else:
            if self.verbose:
                print("Stop iteration. Didnt find",\
                    kwargs['id'],start_ts_ms,end_ts_ms,\
                    "Get errors from upstream now")
            return self.get_general_upstream(start_ts_ms,end_ts_ms,previter,**kwargs)

        me_start = int(float(me_start))
        me_end = int(float(me_end))

        if self.verbose:
            print("Found block",me_vehid,me_start,me_end)

        # Depending on the start and end of the next block, apply divide and conquer
        # by recursive calls of this function.
        if me_start <= start_ts_ms:
            if me_end < end_ts_ms:
                previter, cnt1 = self.get_general_unixts(start_ts_ms,me_end,previter,**kwargs)
                previter, cnt2 = self.get_general_unixts(me_end+1,end_ts_ms,previter,**kwargs)
                return previter,(cnt1+cnt2)
            return self.get_general_sql(start_ts_ms,end_ts_ms,previter,**kwargs)
        if me_end >= end_ts_ms:
            previter, cnt1 = self.get_general_unixts(start_ts_ms,me_start-1,previter,**kwargs)
            previter, cnt2 = self.get_general_unixts(me_start,end_ts_ms,previter,**kwargs)
            return previter,(cnt1+cnt2)
        previter, cnt1 = self.get_general_unixts(start_ts_ms,me_start-1,previter,**kwargs)
        previter, cnt2 = self.get_general_unixts(me_start,me_end,previter,**kwargs)
        previter, cnt3 = self.get_general_unixts(me_end+1,end_ts_ms,previter,**kwargs)
        return previter,(cnt1+cnt2+cnt3)

    def get_general(self,previter : TuIter,**kwargs) -> Tuple[TuIter,int]:
        """returns data specified by kwargs"""
        start_ts_ms = int(kwargs['start'].timestamp()*1000)
        end_ts_ms = int(kwargs['end'].timestamp()*1000)
        return self.get_general_unixts(start_ts_ms,end_ts_ms,previter,**kwargs)

    def get_faults_timedelta(self,
            veh_id : str,
            start : datetime,
            end : datetime,
            previter : TuIter=None) -> Tuple[TuIter,int]:
        """returns error in between the given datetime objects"""
        meta = {}
        meta['start'] = start
        meta['end'] = end
        meta['table'] = 'error'
        meta['id'] = veh_id
        return self.get_general(previter,**meta)
    def get_faults(self,veh_id : str,tdelta=None,previter : TuIter=None) -> Tuple[TuIter,int]:
        """get_faults method"""
        start, end = start_end_from_tdelta(tdelta,self.tdelta_end)
        return self.get_faults_timedelta(veh_id,start,end,previter)
    def get_history_timedelta(self,
            veh_id : str,
            start : datetime,
            end : datetime,
            previter : TuIter=None) -> Tuple[TuIter,int]:
        """returns error in between the given datetime objects"""
        meta = {}
        meta['start'] = start
        meta['end'] = end
        meta['table'] = 'history'
        meta['id'] = veh_id
        return self.get_general(previter,**meta)
    def get_history(self,veh_id : str,tdelta=None,previter : TuIter=None) -> Tuple[TuIter,int]:
        """get_faults method"""
        start, end = start_end_from_tdelta(tdelta,self.tdelta_end)
        return self.get_history_timedelta(veh_id,start,end,previter)
    def get_candata_timedelta(self,
            veh_id : str,
            start : datetime,
            end : datetime,
            previter : TuIter=None) -> Tuple[TuIter,int]:
        """returns error in between the given datetime objects"""
        meta = {}
        meta['start'] = start
        meta['end'] = end
        meta['table'] = 'candata'
        meta['id'] = veh_id
        return self.get_general(previter,**meta)
    def get_candata(self,veh_id : str,tdelta=None,previter : TuIter=None) -> Tuple[TuIter,int]:
        """get_faults method"""
        start, end = start_end_from_tdelta(tdelta,self.tdelta_end)
        return self.get_candata_timedelta(veh_id,start,end,previter)

"""Module for caching data in sql db"""

import sqlite3
import os.path
import os
from datetime import datetime

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
    time text not null, 
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
    start text, 
    end text,
    primary key(unit, start)
)
'''

CREATE_ERROR_DATA_TABLE = '''
CREATE TABLE error(
    unit text not null, 
    time text not null, 
    spn int not null,
    fmi int not null,
    occurenceCount int,
    name text,
    description text,
    primary key(unit,time)
)
'''

class SqlCache:
    """Sql cache can cache trackunit data in Sqlite DB"""
    def __init__(self,db_file="webdb.db"):
        create_tables = not os.path.isfile(db_file)
        self.web_db_path = db_file
        self._db = sqlite3.connect(self.web_db_path)
        if create_tables:
            cur = self._db.cursor()
            cur.execute(CREATE_HISTORY_TABLE)
            cur.execute(CREATE_HISTORY_META)
            cur.execute(CREATE_ERROR_META_TABLE)
            cur.execute(CREATE_ERROR_DATA_TABLE)
            self._db.commit()
    def clean(self):
        if self._db is not None:
            self._db.close()
            os.remove(self.web_db_path)
            self._db = None
    def get_history(self, unit, start):
        """returns history data of a vehicle with start and end date"""
        cur = self._db.cursor()
        try:
            meta = next(cur.execute(
                f"select * from histmeta where unit='{unit}' and start<='{start}' order by start"))
            print(meta)
        except StopIteration:
            print("no element found")

    def get_candata(self,unit,start):
        """returns history data of a vehicle with start and end date"""
        #tbd
    def get_errors(self, unit, start, end):
        """returns error in between the given datetime objects"""
        cur = self._db.cursor()
        try:
            unit, start, end = next(cur.execute(
                f"select * from errormeta where unit='{unit}' and start<='{start}' order by start"))
            start = datetime.fromtimestamp(float(start))
            end   = datetime.fromtimestamp(float(end))
            return unit, start, end
        except StopIteration:
            cur.execute(f"INSERT INTO errormeta (unit, start, end) VALUES ({unit},{start.timestamp()},{end.timestamp()})")
            self._db.commit()
            
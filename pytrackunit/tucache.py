"""tucache module"""

import sqlite3
import os.path
from .webcache import WebCache

class TuCache:
    """tucache class"""
    def __init__(self,auth=None,_dir=None,use_sqlite=False,verbose=False):
        self.cache = WebCache(auth=auth,_dir=_dir,verbose=verbose)
        self.use_sqlite = use_sqlite
        if self.use_sqlite:
            self.web_db_path = os.path.join(_dir,"webdb.db")
            self._db = sqlite3.connect(self.web_db_path)
            cur = self._db.cursor()
            _res = list(cur.execute(
                '''
                SELECT name FROM sqlite_master WHERE type="table" AND name="history"
                '''))
            if len(_res) == 0:
                cur.execute('''CREATE TABLE history
                (unit text not null, time text not null, event int, keyId text, location text, address text, heading int, speed real, 
                km real, run1 real,run2 real,run3 real,run4 real,runOdo real,temperature1 real,temperature2 real,
                input1 int,input2 int,input3 int,input4 int,input5 int,input6 int,input7 int,input8 int,input9 int,input10 int,
                output1 int,output2 int,output3 int,output4 int,output5 int,
                analogInput1 real,analogInput2 real,analogInput4 real,
                Input1ChangeCounter INT,Input2ChangeCounter INT,Input3ChangeCounter INT,Input4ChangeCounter INT,
                batteryLevel real,externalPower real,
                primary key (unit,time))''')
                self._db.commit()
    def clean(self):
        """deletes all cached data"""
        self.cache.clean()
    def get(self,url):
        """takes the data from cache if possible. otherwise data is loaded from web"""
        data = self.cache.get(url)
        if self.cache.return_only_cache_files:
            return [data]
        if self.cache.dont_return_data:
            return []
        if self.cache.dont_read_files and len(data) == 0:
            return []
        # if self.use_sqlite and "api.trackunit.com/public/Report/UnitHistory" in url:
        #     cur = self.db.cursor()
        #     _data = list(map(lambda x: (x["time"])))
        return data.get('list')

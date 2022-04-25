"""module TrackUnit"""

import json
import os.path
import asyncio
import tqdm
from .tucache import TuCache
from .sqlcache import SqlCache
from .helper import SecureString

def get_multi_general(func,idlist,tdelta,f_process=None,progress_bar=True):
    """
    returns the data of a list of vehicles with the ids provided in idlist.
    f_process can be specified to process slices of data. f_process returns a list
    """
    if f_process is None:
        f_process = lambda x, meta: x

    async def get_data_async(globit,globlen):
        _cor = []
        if progress_bar:
            pbar = tqdm.tqdm(total=globlen)
        async for _f, meta in globit:
            _cor += f_process(_f, meta)
            if progress_bar:
                pbar.update()
        return _cor

    globlen = 0
    last = None
    for _id in idlist:
        last,_l = func(_id,tdelta,last)
        globlen += _l

    data = asyncio.run(get_data_async(last,globlen))

    return data

class TrackUnit:
    """TrackUnit class"""
    def __init__(self,**kwargs):
        config_filename = kwargs.get("config_path","config.json")
        config = {}
        if os.path.isfile(config_filename):
            with open(config_filename,encoding="utf8") as file:
                config = json.load(file)
        for k in config:
            if k not in kwargs:
                kwargs[k] = config[k]
        if 'auth' not in kwargs:
            if kwargs.get('api_key',None) is None:
                if 'apikey_path' not in kwargs:
                    kwargs['apikey_path'] = 'api.key'
                with open(kwargs["apikey_path"],encoding="utf8") as file_apikey:
                    api_key = SecureString(file_apikey.readline())
            else:
                api_key = kwargs['api_key']
            if len(api_key.gets()) != 32:
                raise Exception("Invalid API-key length")
            kwargs['auth'] = (SecureString('API'),api_key)
        if kwargs.get('tu_use_sqlcache',False):
            self.cache = SqlCache(**kwargs)
        else:
            self.cache = TuCache(**kwargs)
    async def _a_get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        data = await self.cache.get_unitlist()
        if _type is not None:
            data = list(filter(lambda x: " " in x['name'] and _type in x['name'],data))
        if sort_by_hours:
            if not isinstance(data,list):
                data = list(data)
            data.sort(key=lambda x: (x['run1'] if 'run1' in x else 0),reverse=True)
        return data

    def get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        return asyncio.run(self._a_get_unitlist(_type,sort_by_hours))

    async def _a_get_history(self,veh_id,tdelta):
        """async getHistory method"""
        data = []
        _it, _ = self.cache.get_history(veh_id,tdelta)
        async for _d,_ in _it:
            data += _d
        return data

    async def _a_get_candata(self,veh_id,tdelta=None):
        """async getCanData method"""
        data = []
        _it, _ = self.cache.get_candata(veh_id,tdelta)
        async for _d,_ in _it:
            data += _d
        return data

    async def _a_get_faults(self,veh_id,tdelta=None):
        """async get_faults method"""
        data = []
        _it, _ = self.cache.get_faults(veh_id,tdelta)
        async for _d,_ in _it:
            data += _d
        return data

    def get_history(self,veh_id,tdelta):
        """getHistory method"""
        return asyncio.run(self._a_get_history(veh_id,tdelta))

    def get_candata(self,veh_id,tdelta=None):
        """getCanData method"""
        return asyncio.run(self._a_get_candata(veh_id,tdelta))

    def get_faults(self,veh_id,tdelta=None):
        """get_faults method"""
        return asyncio.run(self._a_get_faults(veh_id,tdelta))

    def get_multi_history(self,idlist,tdelta,f_process=None,progress_bar=True):
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        return get_multi_general(
            self.cache.get_history,idlist,tdelta,f_process,progress_bar)

    def get_multi_candata(self,idlist,tdelta,f_process=None,progress_bar=True):
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        return get_multi_general(
            self.cache.get_candata,idlist,tdelta,f_process,progress_bar)

    def get_multi_faults(self,idlist,tdelta,f_process=None,progress_bar=True):
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        return get_multi_general(
            self.cache.get_faults,idlist,tdelta,f_process,progress_bar)

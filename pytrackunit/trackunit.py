"""module TrackUnit"""

import json
import os.path
import asyncio
import tqdm
from .tucache import TuCache

def get_multi_general(func,idlist,tdelta,f_process=None,progress_bar=True):
    """
    returns the data of a list of vehicles with the ids provided in idlist.
    f_process can be specified to process slices of data. f_process returns a list
    """
    if f_process is None:
        f_process = lambda x: x

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
    def __init__(self,config_filename=None,api_key=None,verbose=False):
        if config_filename is None:
            config_filename = "config.json"
        config = {}
        if os.path.isfile(config_filename):
            with open(config_filename,encoding="utf8") as file:
                config = json.load(file)
        else:
            config["apikey-location"] = "api.key"
            config["webcache-location"] = "web-cache"
        if api_key is None:
            with open(config["apikey-location"],encoding="utf8") as file_apikey:
                api_key = file_apikey.readline()
        self.cache = TuCache(('API',api_key),_dir=config["webcache-location"],verbose=verbose)

    @property
    def verbose(self):
        """returns verbose mode value. in verbose mode, diagnostic output is printed to console."""
        return self.cache.cache.verbose
    @verbose.setter
    def verbose(self, value):
        """sets the verbose mode. in verbose mode, diagnostic output is printed to console."""
        self.cache.cache.verbose = value

    def get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        data = asyncio.run(self.cache.get_url('Unit'))
        if _type is not None:
            data = list(filter(lambda x: " " in x['name'] and _type in x['name'],data))
        if sort_by_hours:
            data.sort(key=lambda x: (x['run1'] if 'run1' in x else 0),reverse=True)
        return data

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

    def get_history(self,veh_id,tdelta):
        """getHistory method"""
        return asyncio.run(self._a_get_history(veh_id,tdelta))

    def get_candata(self,veh_id,tdelta=None):
        """getCanData method"""
        return asyncio.run(self._a_get_candata(veh_id,tdelta))

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

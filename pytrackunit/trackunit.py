"""module TrackUnit"""

import json
import os.path
import asyncio
from .tucache import TuCache

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
        async for _d in _it:
            data += _d
        return data

    async def _a_get_candata(self,veh_id,tdelta=None):
        """async getCanData method"""
        data = []
        _it, _ = self.cache.get_candata(veh_id,tdelta)
        async for _d in _it:
            data += _d
        return data

    def get_history(self,veh_id,tdelta):
        """getHistory method"""
        return asyncio.run(self._a_get_history(veh_id,tdelta))

    def get_candata(self,veh_id,tdelta=None):
        """getCanData method"""
        return asyncio.run(self._a_get_candata(veh_id,tdelta))

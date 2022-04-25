"""webcache module"""

import traceback
import json
import os
from os.path import join
from hashlib import md5
from pathlib import Path
import shutil
import aiohttp
import aiofiles
from aiohttp.helpers import BasicAuth

async def get_from_file(fname,dont_read=False):
    """get_from_file method"""
    try:
        if os.path.isfile(fname):
            if dont_read:
                return {}
            try:
                async with aiofiles.open(fname,encoding='utf8') as file:
                    content = await file.read()
                return json.loads(content)
            except json.JSONDecodeError:
                print("Error at TUCache get_from_file(1):\n"+str(traceback.format_exc()))
                try:
                    os.remove(fname)
                except OSError:
                    print("Error at TUCache get_from_file(3):\n"+str(traceback.format_exc()))
                return None
        else:
            return None
    except OSError:
        print("Error at TUCache get_from_file(2):\n"+str(traceback.format_exc()))
        return None

class WebCache:
    """WebCache class"""
    def __init__(self,**kwargs):
        if kwargs.get('verbose',False):
            print("WebCaches args:",kwargs)
        auth_tuple = kwargs.get("auth",None)
        self.auth = BasicAuth(auth_tuple[0].gets(),auth_tuple[1].gets()) \
            if auth_tuple is not None else None
        self.verbose = kwargs.get("verbose",False)
        self.dir = kwargs.get("webcache_dir","web-cache")
        self.dont_read_files = kwargs.get("dont_read_files",False)
        self.dont_return_data = kwargs.get("dont_return_data",False)
        self.return_only_cache_files = kwargs.get("return_only_cache_files",False)
        self.dont_cache_data = kwargs.get("dont_cache_data",False)
        Path(self.dir).mkdir(parents=True, exist_ok=True)
    def clean(self):
        """clean method"""
        try:
            shutil.rmtree(self.dir)
        except OSError:
            print("Error at TUCache clean:\n"+str(traceback.format_exc()))
        Path(self.dir).mkdir(parents=True, exist_ok=True)
    async def get_from_web(self,url: str) -> dict:
        """get_from_web method"""
        async with aiohttp.ClientSession() as session:
            async with session.request('GET', url,auth=self.auth) as response:
                response.raise_for_status()
                _j = await response.json()
                _t = await response.text()
                return _j , _t
    async def get(self,url):
        """get method"""
        if self.dont_cache_data:
            data, _ = await self.get_from_web(url)
            return data
        fname = md5(url.encode('utf-8')).hexdigest()+".json"
        if self.return_only_cache_files:
            return fname
        fname = join(self.dir,fname)
        data = await get_from_file(fname,self.dont_read_files)
        if data is None:
            data, text = await self.get_from_web(url)
            async with aiofiles.open(fname, mode='w+',encoding='utf8') as _fp:
                await _fp.write(text)
            if self.verbose:
                print(url,len(text),"W")
        else:
            if self.verbose:
                print(url,len(str(data)),"C")
        if self.dont_return_data:
            return {}
        return data

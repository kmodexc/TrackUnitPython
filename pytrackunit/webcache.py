"""webcache module"""

import traceback
import json
import os
from os.path import join
from hashlib import md5
from pathlib import Path
import shutil
import requests

def get_from_file(fname,dont_read=False):
    """get_from_file method"""
    try:
        if os.path.isfile(fname):
            if dont_read:
                return {}
            try:
                with open(fname,encoding='utf8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("Error at TUCache get_from_file(1):\n"+str(traceback.format_exc()))
                try:
                    os.remove(fname)
                except OSError:
                    pass
                return None
        else:
            return None
    except OSError:
        print("Error at TUCache get_from_file(2):\n"+str(traceback.format_exc()))
        return None

class WebCache:
    """WebCache class"""
    def __init__(self,auth=None,_dir=None,verbose=False):
        self.auth = auth
        self.verbose = verbose
        if _dir is None:
            self.dir = "web-cache"
        else:
            self.dir = _dir
        self.min_write_len = 0
        self.dont_read_files = False
        Path(self.dir).mkdir(parents=True, exist_ok=True)
    def clean(self):
        """clean method"""
        try:
            shutil.rmtree(self.dir)
        except OSError:
            print("Error at TUCache clean:\n"+str(traceback.format_exc()))
        Path(self.dir).mkdir(parents=True, exist_ok=True)
    def get_from_web(self,url):
        """get_from_web method"""
        resp = requests.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise Exception(
                "Could not get data from server (http error) code "+str(resp.status_code))
        return resp
    def get(self,url):
        """get method"""
        fname = join(self.dir,md5(url.encode('utf-8')).hexdigest()+".json")
        data = get_from_file(fname,self.dont_read_files)
        if data is None:
            resp = self.get_from_web(url)
            if len(resp.text) > self.min_write_len:
                with open(fname,'w',encoding='utf8') as file:
                    file.write(resp.text)
            data = resp.json()
            if self.verbose:
                print(url,len(str(data)),"W")
        else:
            if self.verbose:
                print(url,len(str(data)),"C")
        return data

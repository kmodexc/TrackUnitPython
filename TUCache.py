import requests
from os.path import join
from hashlib import md5
from pathlib import Path
import traceback
import json
import os

class TUCache:
    def __init__(self,auth=None,dir=None):
        self.auth = auth
        if dir is None:
            self.dir = "web-cache"
        else:
            self.dir = dir
        self.min_write_len = 0
        Path(self.dir).mkdir(parents=True, exist_ok=True)
    def clean(self):
        try:
            os.remove(self.dir)
        except Exception:
            print("Error at TUCache clean:\n"+str(traceback.format_exc()))
        Path(self.dir).mkdir(parents=True, exist_ok=True)
    def get_from_file(self,fname):
        try:
            if os.path.exists(fname):
                try:
                    with open(fname,encoding='utf8') as f:
                        return json.load(f)
                except Exception:
                    print("Error at TUCache get_from_file(1):\n"+str(traceback.format_exc()))
                    try:
                        os.remove(fname)
                    except:
                        pass
                    return None
            else:
                return None
        except Exception:
            print("Error at TUCache get_from_file(2):\n"+str(traceback.format_exc()))
            return None
    def get_from_web(self,url):
        resp = requests.get(url, auth=self.auth)
        if resp.status_code != 200:
            raise Exception("Could not get data from server (http error) code "+str(resp.status_code))
        return resp
    def get(self,url):
        fname = join(self.dir,md5(url.encode('utf-8')).hexdigest()+".json")
        data = self.get_from_file(fname)
        if data is None:
            resp = self.get_from_web(url)
            if len(resp.text) > self.min_write_len:
                with open(fname,'w',encoding='utf8') as f:
                    f.write(resp.text)
            data = resp.json()
        return data
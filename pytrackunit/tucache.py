"""tucache module"""

from .webcache import WebCache

class TuCache:
    """tucache class"""
    def __init__(self,auth=None,_dir=None):
        self.cache = WebCache(auth=auth,_dir=_dir)
    def clean(self):
        """deletes all cached data"""
        self.cache.clean()
    def get(self,url):
        """takes the data from cache if possible. otherwise data is loaded from web"""
        return self.cache.get(url)

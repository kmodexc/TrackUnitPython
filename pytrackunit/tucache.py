"""tucache module"""

from datetime import timedelta
from math import ceil
from .webcache import WebCache
from .tuiter import ReqIter, TuIter
from .helper import start_end_from_tdelta

URL_BASE = r'https://api.trackunit.com/public/'

class TuCache:
    """tucache class"""
    def __init__(self,**kwargs):
        self.cache = WebCache(**kwargs)
        self.settings = kwargs
        self.settings.setdefault('req_period',30)
        self.settings.setdefault('tdelta_end',None)
        self.settings.setdefault('return_only_cache_files',False)
        self.settings.setdefault('dont_return_data',False)
        self.settings.setdefault('dont_read_files',False)
    def clean(self):
        """deletes all cached data"""
        self.cache.clean()
    async def get_url(self,url):
        """takes the data from cache if possible. otherwise data is loaded from web"""
        data = await self.cache.get(URL_BASE+url)
        if self.settings['return_only_cache_files']:
            return [data]
        if self.settings['dont_return_data']:
            return []
        if self.settings['dont_read_files'] and len(data) == 0:
            return []
        return data.get('list')
    async def get_unitlist(self):
        """returns a list of vehicles"""
        return await self.get_url('Unit')
    def general_daydiff_get(self,furl,meta,previter=None):
        """returns data for timedependant requests for a given daydelta"""
        tdelta = meta["tdelta"]
        start,end = start_end_from_tdelta(tdelta,self.settings['tdelta_end'])
        meta["start"] = start
        meta["end"] = end
        return self.general_time_range_get(furl,meta,previter)
    def general_time_range_get(self,furl,meta,previter=None):
        """returns data for timedependant requests for a start and enddate"""
        start = meta["start"]
        end = meta["end"]
        days = (end-start).days
        req_period = self.settings['req_period']
        requests = []
        for week in range(ceil(days/req_period)):
            wstart = start+timedelta(days=week*req_period)
            wend = wstart+timedelta(days=min(req_period,(end-wstart).days))
            requests.append(furl(\
                wstart.strftime("%Y-%m-%dT%H:%M:%S"),\
                wend.strftime("%Y-%m-%dT%H:%M:%S")))
        internal_iter = ReqIter(self,iter(requests),meta)
        if previter is None:
            previter = TuIter()
        previter.add(internal_iter)
        return previter,len(requests)

    def get_history(self,veh_id,tdelta,previter=None):
        """getHistory method"""
        meta = {}
        meta["id"] = veh_id
        meta["tdelta"] = tdelta
        return self.general_daydiff_get(lambda t1,t2: \
            'Report/UnitHistory?unitId='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                meta,previter)
    def get_history_timedelta(self,veh_id,start,end,previter=None):
        """getHistory method"""
        meta = {}
        meta["id"] = veh_id
        meta["start"] = start
        meta["end"] = end
        return self.general_time_range_get(lambda t1,t2: \
            'Report/UnitHistory?unitId='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                meta,previter)
    def get_candata(self,veh_id,tdelta=None,previter=None):
        """getCanData method"""
        meta = {}
        meta["id"] = veh_id
        meta["tdelta"] = tdelta
        return self.general_daydiff_get(lambda t1,t2: \
            'Report/UnitExtendedInfo?Id='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                meta,previter)
    def get_candata_timedelta(self,veh_id,start,end,previter=None):
        """getCanData method"""
        meta = {}
        meta["id"] = veh_id
        meta["start"] = start
        meta["end"] = end
        return self.general_time_range_get(lambda t1,t2: \
            'Report/UnitExtendedInfo?Id='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                meta,previter)
    def get_faults(self,veh_id,tdelta=None,previter=None):
        """get_faults method"""
        meta = {}
        meta["id"] = veh_id
        meta["tdelta"] = tdelta
        return self.general_daydiff_get(lambda t1,t2: \
            'Report/UnitActiveFaults?id='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                meta,previter)
    def get_faults_timedelta(self,veh_id,start,end,previter=None):
        """get_faults method"""
        meta = {}
        meta["id"] = veh_id
        meta["start"] = start
        meta["end"] = end
        return self.general_time_range_get(lambda t1,t2: \
            'Report/UnitActiveFaults?id='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                meta,previter)

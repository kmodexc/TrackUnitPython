"""module TrackUnit"""

from math import ceil
from multiprocessing import Pool
from datetime import timedelta,datetime
from .tucache import TuCache

class TrackUnit:
    """TrackUnit class"""
    def __init__(self,api_key=None,verbose=False):
        if api_key is None:
            with open("api.key",encoding="utf8") as file:
                api_key = file.readline()
        self.cache = TuCache(('API',api_key),verbose=verbose)
        self.verbose = verbose
        self.req_period = 30
        self.tdelta_end = None
    def get(self,req):
        """get method"""
        url = r'https://api.trackunit.com/public/'+req
        resp = self.cache.get(url)
        data = resp.get('list')
        if data is None:
            raise Exception("no data: "+str(resp))
        return data
    def get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        data = self.get('Unit')
        if _type is not None:
            data = list(filter(lambda x: " " in x['name'] and _type in x['name'],data))
        if sort_by_hours:
            data.sort(key=lambda x: (x['run1'] if 'run1' in x else 0),reverse=True)
        return data
    def general_daydiff_get(self,furl,tdelta,threads=1):
        """returns data for timedependant requests for a given daydelta"""
        if self.tdelta_end is None:
            end = datetime.now()
        else:
            end = self.tdelta_end
        end = end.replace(hour=0,minute=0,second=0,microsecond=0)
        if isinstance(tdelta,datetime):
            start = end+tdelta
        else:
            irange = int(tdelta)
            if irange <= 0:
                return []
            start = end-timedelta(days=irange)
        return self.general_time_range_get(furl,start,end,threads)
    def general_time_range_get(self,furl,start=None,end=None,threads=1):
        """returns data for timedependant requests for a start and enddate"""
        total_data = []
        days = (end-start).days
        requests = []
        for week in range(ceil(days/self.req_period)):
            wstart = start+timedelta(days=week*self.req_period)
            wend = wstart+timedelta(days=min(self.req_period,(end-wstart).days))
            requests.append(furl(\
                wstart.strftime("%Y-%m-%dT%H:%M:%S"),\
                wend.strftime("%Y-%m-%dT%H:%M:%S")))
        if threads > 1:
            with Pool(threads) as _p:
                map_result = _p.map(self.get,requests)
        else:
            map_result = map(self.get,requests)
        for _r in map_result:
            total_data += _r
        return total_data
    def get_history(self,veh_id,tdelta,threads=1):
        """getHistory method"""
        return self.general_daydiff_get(lambda t1,t2: \
            'Report/UnitHistory?unitId='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                tdelta,threads)
    def get_candata(self,veh_id,tdelta=None,threads=1):
        """getCanData method"""
        return self.general_daydiff_get(lambda t1,t2: \
            'Report/UnitExtendedInfo?Id='+veh_id+'&from='+t1+'.0000001Z&to='+t2+'.0000000Z',\
                tdelta,threads)

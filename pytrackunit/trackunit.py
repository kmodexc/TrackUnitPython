"""module TrackUnit"""

from math import ceil
from multiprocessing import Pool
from datetime import timedelta,datetime
from . import tucache

class TrackUnit:
    """TrackUnit class"""
    def __init__(self,api_key=None,verbose=False):
        if api_key is None:
            with open("api.key",encoding="utf8") as file:
                api_key = file.readline()
        self.cache = tucache.TuCache(('API',api_key))
        self.verbose = verbose
        self.req_period = 30
    def get(self,req):
        """get method"""
        url = r'https://api.trackunit.com/public/'+req
        resp = self.cache.get(url)
        data = resp.get('list')
        if data is None:
            raise Exception("no data: "+str(resp))
        if self.verbose:
            print(req+"\t"+str(len(data)))
        return data
    def get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        data = self.get('Unit')
        if _type is not None:
            data = list(filter(lambda x: " " in x['name'] and _type in x['name'],data))
        if sort_by_hours:
            data.sort(key=lambda x: (x['run1'] if 'run1' in x else 0),reverse=True)
        return data
    def get_history(self,veh_id,tdelta=None,start=None,end=None,threads=1):
        """getHistory method"""
        total_data = []
        if tdelta is None and start is not None and end is not None:
            days = (end-start).days
            requests = []
            request_period = self.req_period
            for week in range(ceil(days/request_period)):
                wstart = start+timedelta(days=week*request_period)
                wstartstr = wstart.strftime("%Y-%m-%dT%H:%M:%S")
                wend = wstart+timedelta(days=min(request_period,(end-wstart).days))
                wendstr = wend.strftime("%Y-%m-%dT%H:%M:%S")
                req = 'Report/UnitHistory?unitId='+veh_id+'&from='+wstartstr+\
                    '.0000001Z&to='+wendstr+'.0000000Z'
                requests.append(req)
            if threads > 1:
                with Pool(threads) as _p:
                    map_result = _p.map(self.get,requests)
            else:
                map_result = map(self.get,requests)
            for _r in map_result:
                total_data += _r
        elif tdelta is not None and start is None and end is None:
            end = datetime.now()
            end = end.replace(hour=0,minute=0,second=0,microsecond=0)
            if isinstance(tdelta,datetime):
                start = end+tdelta
            else:
                irange = int(tdelta)
                if irange <= 0:
                    return []
                start = end-timedelta(days=irange)
            total_data = self.get_history(veh_id,None,start,end,threads)
        else:
            raise Exception("invalid argument combination of tdelta,start,end")
        return total_data
    def get_candata(self,veh_id,tdelta=None,start=None,end=None,threads=1):
        """getCanData method"""
        total_data = []
        if tdelta is None and start is not None and end is not None:
            days = (end-start).days
            requests = []
            request_period = self.req_period
            for week in range(ceil(days/request_period)):
                wstart = start+timedelta(days=week*request_period)
                wstartstr = wstart.strftime("%Y-%m-%dT%H:%M:%S")
                wend = wstart+timedelta(days=min(request_period,(end-wstart).days))
                wendstr = wend.strftime("%Y-%m-%dT%H:%M:%S")
                req = 'Report/UnitExtendedInfo?Id='+veh_id+'&from='+wstartstr+\
                    '.0000001Z&to='+wendstr+'.0000000Z'
                requests.append(req)
            if threads > 1:
                with Pool(threads) as _p:
                    map_result = _p.map(self.get,requests)
            else:
                map_result = map(self.get,requests)
            for _r in map_result:
                total_data += _r
        elif tdelta is not None and start is None and end is None:
            end = datetime.now()
            end = end.replace(hour=0,minute=0,second=0,microsecond=0)
            if isinstance(tdelta,datetime):
                start = end+tdelta
            else:
                irange = int(tdelta)
                if irange <= 0:
                    return []
                start = end-timedelta(days=irange)
            total_data = self.get_candata(veh_id,None,start,end,threads)
        else:
            raise Exception("invalid argument combination of tdelta,start,end")
        return total_data

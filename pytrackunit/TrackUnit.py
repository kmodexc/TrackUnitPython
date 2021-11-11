from datetime import timedelta,datetime
from . import TUCache
from math import ceil
from threading import Thread
from multiprocessing import Pool

class TrackUnit:
    def __init__(self,api_key=None,verbose=False):
        if api_key is None:
            api_key = open("api.key").readlines()[0]
        self.cache = TUCache.TUCache(('API',api_key))
        self.verbose = verbose
        self.req_period = 30
    def get(self,req):
        url = r'https://api.trackunit.com/public/'+req
        resp = self.cache.get(url)
        data = resp.get('list')
        if data is None:
            raise Exception("no data: "+str(resp))
        if self.verbose:
            print(req+"\t"+str(len(data)))
        return data
    def unitList(self,type=None,sortByHours=True):
        data = self.get('Unit')
        if type is not None:
            data = list(filter(lambda x: " " in x['name'] and type in x['name'],data))
        if sortByHours:
            data.sort(key=lambda x: (x['run1'] if 'run1' in x else 0),reverse=True)
        return data
    def getHistory(self,vehId,tdelta=None,start=None,end=None,threads=1):
        if tdelta is None and start is not None and end is not None:
            days = (end-start).days
            requests = []
            request_period = self.req_period
            for week in range(ceil(days/request_period)):
                wstart = start+timedelta(days=week*request_period)
                wstartstr = wstart.strftime("%Y-%m-%dT%H:%M:%S")
                wend = wstart+timedelta(days=min(request_period,(end-wstart).days))
                wendstr = wend.strftime("%Y-%m-%dT%H:%M:%S")
                req = 'Report/UnitHistory?unitId='+vehId+'&from='+wstartstr+'.0000001Z&to='+wendstr+'.0000000Z'
                requests.append(req)                
            if threads > 1:
                with Pool(threads) as p:
                    map_result = p.map(self.get,requests)
            else:
                map_result = map(self.get,requests)
            totalData = []
            for r in map_result:
                totalData += r            
            return totalData
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
            return self.getHistory(vehId,None,start,end,threads)
        else:
            raise Exception("invalid argument combination of tdelta,start,end")
    def getCanData(self,vehId,tdelta=None,start=None,end=None,threads=1):
        if tdelta is None and start is not None and end is not None:
            days = (end-start).days
            requests = []
            request_period = self.req_period
            for week in range(ceil(days/request_period)):
                wstart = start+timedelta(days=week*request_period)
                wstartstr = wstart.strftime("%Y-%m-%dT%H:%M:%S")
                wend = wstart+timedelta(days=min(request_period,(end-wstart).days))
                wendstr = wend.strftime("%Y-%m-%dT%H:%M:%S")
                req = 'Report/UnitExtendedInfo?Id='+vehId+'&from='+wstartstr+'.0000001Z&to='+wendstr+'.0000000Z'
                requests.append(req)                
            if threads > 1:
                with Pool(threads) as p:
                    map_result = p.map(self.get,requests)
            else:
                map_result = map(self.get,requests)
            totalData = []
            for r in map_result:
                totalData += r            
            return totalData
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
            return self.getCanData(vehId,None,start,end,threads)
        else:
            raise Exception("invalid argument combination of tdelta,start,end")

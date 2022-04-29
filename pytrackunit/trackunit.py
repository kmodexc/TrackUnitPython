"""module TrackUnit"""

import json
import os.path
import asyncio
from typing import Callable, Iterable

import tqdm
import aioprocessing

from .tuiter import TuIter
from .tucache import TuCache
from .sqlcache import SqlCache
from .helper import SecureString


async def async_queue_generator(queue : aioprocessing.AioQueue):
    """converts the queue into an generator"""
    while True:
        obj = await queue.coro_get()
        if obj is None:
            break
        yield obj

def queue_generator(queue : aioprocessing.AioQueue):
    """converts the queue into an generator"""
    while True:
        obj = queue.get()
        if obj is None:
            break
        yield obj

async def async_collect_data(
        queue : aioprocessing.AioQueue,
        tuit : TuIter,
        f_process : Callable[[Iterable[dict],dict],Iterable],
        progress_bar : tqdm.tqdm=None) -> None:
    """
    Collects the data from tuiter and puts it in a async queue.
    If set it will call update of the progress_bar after each iteration.
    """


    async for data_list, meta in tuit:
        proc_data = f_process(data_list,meta)
        for _x in proc_data:
            if _x is not None:
                await queue.coro_put(_x)
        if progress_bar is not None:
            progress_bar.update()


async def async_provider_process(
        settings : dict,
        queue : aioprocessing.AioQueue,
        veh_id_list : Iterable[str],
        tdelta : int,
        str_function : str) -> None:
    """
    puts the data it gets from trackunit and puts it in the given queue
    function can be "error" "history" "candata"
    """
    if settings['verbose']:
        print("Provider process started")

    _tu = TrackUnit(**settings)

    if str_function == "history":
        f_function = _tu.cache.get_history
    elif str_function == "candata":
        f_function = _tu.cache.get_candata
    else:
        f_function = _tu.cache.get_faults

    await _tu.async_get_multi_general_queue(queue,f_function,veh_id_list,tdelta)

def provider_process(
        settings : dict,
        queue : aioprocessing.AioQueue,
        veh_id_list : Iterable[str],
        tdelta : int,
        str_function : str) -> None:
    """
    puts the data it gets from trackunit and puts it in the given queue
    function can be "error" "history" "candata"
    """
    asyncio.run(async_provider_process(settings,queue,veh_id_list,tdelta,str_function))

class TrackUnit:
    """TrackUnit class"""
    def __init__(self,**kwargs):
        config_filename = kwargs.get("config_path","config.json")
        config = {}
        if os.path.isfile(config_filename):
            with open(config_filename,encoding="utf8") as file:
                config = json.load(file)
        for k in config:
            if k not in kwargs:
                kwargs[k] = config[k]
        if 'auth' not in kwargs:
            if kwargs.get('api_key',None) is None:
                if 'apikey_path' not in kwargs:
                    kwargs['apikey_path'] = 'api.key'
                with open(kwargs["apikey_path"],encoding="utf8") as file_apikey:
                    api_key = SecureString(file_apikey.readline())
            else:
                api_key = kwargs['api_key']
            if len(api_key.gets()) != 32:
                raise Exception("Invalid API-key length")
            kwargs['auth'] = (SecureString('API'),api_key)
        if kwargs.get('tu_use_sqlcache',False):
            self.cache = SqlCache(**kwargs)
        else:
            self.cache = TuCache(**kwargs)
        self.settings = kwargs
        self.settings.setdefault("use_progress_bar",True)
        self.settings.setdefault("queue_size",1000)
        self.settings.setdefault("use_async_generator",False)

    async def async_get_multi_general_queue(
            self,
            queue : aioprocessing.AioQueue,
            func : Callable,
            idlist : Iterable[str],
            tdelta : int) -> None:
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """

        f_process = lambda x, meta: zip(x,[meta.get('id','no-id-found')])

        iterators = []

        globlen = 0
        for _id in idlist:
            _it,_l= func(_id,tdelta)
            globlen += _l
            iterators.append(_it)

        if self.settings['use_progress_bar']:
            pbar = tqdm.tqdm(total=globlen)
        else:
            pbar = None

        zipped_list = list(zip(
            len(iterators)*[queue],
            iterators,
            len(iterators)*[f_process],
            len(iterators)*[pbar]))

        tasks = list(map(lambda x: async_collect_data(*x),zipped_list))

        if self.settings['verbose']:
            print("async_get_multi_general_queue created tasks")

        await asyncio.gather(*tasks)

        if self.settings['verbose']:
            print("async_get_multi_general_queue tasks finished")

        await queue.coro_put(None)

    def get_multi_general(
            self,
            idlist : Iterable[str],
            tdelta : int,
            str_process : str,
            use_async_generator : bool) -> Iterable:
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        queue = aioprocessing.AioQueue(self.settings['queue_size'])
        worker = aioprocessing.AioProcess(
            target=provider_process,
            args=(self.settings,queue,idlist,tdelta,str_process))
        # pylint: disable=no-member
        worker.start()
        # pylint: enable=no-member
        if use_async_generator:
            return async_queue_generator(queue)
        return queue_generator(queue)

    async def async_get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        data = await self.cache.get_unitlist()
        if _type is not None:
            data = list(filter(lambda x: " " in x['name'] and _type in x['name'],data))
        if sort_by_hours:
            if not isinstance(data,list):
                data = list(data)
            data.sort(key=lambda x: (x['run1'] if 'run1' in x else 0),reverse=True)
        return data

    def get_unitlist(self,_type=None,sort_by_hours=True):
        """unitList method"""
        return asyncio.run(self.async_get_unitlist(_type,sort_by_hours))

    async def async_get_history(self,veh_id,tdelta):
        """async getHistory method"""
        data = []
        _it, _ = self.cache.get_history(veh_id,tdelta)
        async for _d,_ in _it:
            data += _d
        return data

    async def async_get_candata(self,veh_id,tdelta=None):
        """async getCanData method"""
        data = []
        _it, _ = self.cache.get_candata(veh_id,tdelta)
        async for _d,_ in _it:
            data += _d
        return data

    async def async_get_faults(self,veh_id,tdelta=None):
        """async get_faults method"""
        data = []
        _it, _ = self.cache.get_faults(veh_id,tdelta)
        async for _d,_ in _it:
            data += _d
        return data

    def get_history(self,veh_id,tdelta):
        """getHistory method"""
        return asyncio.run(self.async_get_history(veh_id,tdelta))

    def get_candata(self,veh_id,tdelta=None):
        """getCanData method"""
        return asyncio.run(self.async_get_candata(veh_id,tdelta))

    def get_faults(self,veh_id,tdelta=None):
        """get_faults method"""
        return asyncio.run(self.async_get_faults(veh_id,tdelta))

    def get_multi_history(self,idlist,tdelta):
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        return self.get_multi_general(
            idlist,tdelta,"history",self.settings['use_async_generator'])

    def get_multi_candata(self,idlist,tdelta):
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        return self.get_multi_general(
            idlist,tdelta,"candata",self.settings['use_async_generator'])

    def get_multi_faults(self,idlist,tdelta):
        """
        returns the data of a list of vehicles with the ids provided in idlist.
        f_process can be specified to process slices of data. f_process returns a list
        """
        return self.get_multi_general(
            idlist,tdelta,"error",self.settings['use_async_generator'])

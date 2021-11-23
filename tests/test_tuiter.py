import asyncio
from pytrackunit.tuiter import ReqIter, TuIter

class CacheForTests:
	"""tucache class"""
	def __init__(self):
		self.urls = []
	def clean(self):
		self._clean = True
	async def get_url(self,url):
		self._clean = False
		self.urls.append(url)
		return url

async def run(_it):
    data = []
    metal = []
    async for f,meta in _it:
        print(f,meta)
        data.append(f)
        metal.append(meta)
    return data, metal

def test_tuiter():
    cache = CacheForTests()
    _it1 = ReqIter(cache,iter(["1","2","3"]))
    _it2 = ReqIter(cache,iter(["4","5","6"]))
    _itmain = TuIter()
    _itmain.add(_it1)
    _itmain.add(_it2)
    data,meta = asyncio.run(run(_itmain))
    assert len(data) == 6
    for i in range(1,6):
        assert str(i) in data
    assert len(meta) == 6
    for i in meta:
        assert i is None

def test_meta():
    cache = CacheForTests()
    meta1 = {}
    meta1["test"] = "val1"
    meta2 = {}
    meta2["test"] = "val2"
    _it1 = ReqIter(cache,iter(["1","2","3"]),meta1)
    _it2 = ReqIter(cache,iter(["4","5","6"]),meta2)
    _itmain = TuIter()
    _itmain.add(_it1)
    _itmain.add(_it2)
    data,meta = asyncio.run(run(_itmain))
    assert len(data) == 6
    for i in range(1,6):
        assert str(i) in data
    assert len(meta) == 6
    assert not (meta1 == meta2)
    for i in range(1,6):
        if int(data[i]) <= 3:
            assert meta[i] == meta1
        else:
            assert meta[i] == meta2
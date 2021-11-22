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
    async for f in _it:
        print(f)
        data.append(f)
    return data

def test_tuiter():
    cache = CacheForTests()
    _it1 = ReqIter(cache,iter(["1","2","3"]))
    _it2 = ReqIter(cache,iter(["4","5","6"]))
    _itmain = TuIter()
    _itmain.add(_it1)
    _itmain.add(_it2)
    data = asyncio.run(run(_itmain))
    assert len(data) == 6
    for i in range(1,6):
        assert str(i) in data

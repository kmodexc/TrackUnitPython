from pytrackunit.tucache import TuCache
import asyncio
from datetime import datetime

DUMMY_URL = 'https://api.trackunit.com/public/Unit'
DATA_LEN = 21779
BASE_URL = "https://api.trackunit.com/public/Report/UnitExtendedInfo?Id=3331359"

class CacheForTests:
	"""tucache class"""
	def __init__(self):
		self.return_only_cache_files = False
		self.dont_return_data = False
		self.dont_read_files = False
		self.urls = []
		self._clean = False
		self.testobj = {}
		self.testobj["val"] = 1
		self.retval = {}
		self.retval["list"] = 2*[self.testobj]
	def clean(self):
		self._clean = True
	async def get(self,url):
		self._clean = False
		print(url)
		self.urls.append(url)
		return self.retval

async def tolist(_iter):
	data = []
	async for i in _iter:
		data += i
	return data
def test_clean_start():
	cache = TuCache(_dir="pytest-web-cache")
	cache.clean()
def test_Clean_Dummy():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache = CacheForTests()
	assert not cache.cache._clean
	cache.clean()
	assert cache.cache._clean
def test_Get_Check_Urls():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache = CacheForTests()
	data = asyncio.run(cache.get_url('Unit'))
	assert len(cache.cache.urls) == 1
	assert cache.cache.urls[0] == DUMMY_URL
def test_Get_Check_Return():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache = CacheForTests()
	data = asyncio.run(cache.get_url('Unit'))
	assert len(data) == 2
	assert data[0]["val"] == 1
	assert data[1]["val"] == 1
def test_Get_return_hashes():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache.return_only_cache_files = True
	cache.clean()
	data = asyncio.run(cache.get_url('Unit'))
	assert len(data) == 1
	assert data[0] == "79fb93d6b6a0d19f2fb3b55fc8e19489.json"
def test_getcandata_check_urls():
	cache = TuCache(_dir="pytest-web-cache")
	cache.tdelta_end = datetime(2021,11,15,10,0,0,0)
	cache.cache = CacheForTests()
	_it,_l = cache.get_candata("3331359",tdelta=100)
	assert _l == 4
	asyncio.run(tolist(_it))
	assert len(cache.cache.urls) == 4
	assert cache.cache.urls[0] == BASE_URL+"&from=2021-08-07T00:00:00.0000001Z&to=2021-09-06T00:00:00.0000000Z"
	assert cache.cache.urls[1] == BASE_URL+"&from=2021-09-06T00:00:00.0000001Z&to=2021-10-06T00:00:00.0000000Z"
	assert cache.cache.urls[2] == BASE_URL+"&from=2021-10-06T00:00:00.0000001Z&to=2021-11-05T00:00:00.0000000Z"
	assert cache.cache.urls[3] == BASE_URL+"&from=2021-11-05T00:00:00.0000001Z&to=2021-11-15T00:00:00.0000000Z"

from pytrackunit.tucache import TuCache

DUMMY_URL = 'https://pokeapi.co/api/v2/pokemon/ditto'
DATA_LEN = 21779

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
	def get(self,url):
		self._clean = False
		print(url)
		self.urls.append(url)
		return self.retval

def test_clean_start():
	cache = TuCache(_dir="pytest-web-cache")
	cache.clean()
def test_Get_Clean():
	cache = TuCache(_dir="pytest-web-cache")
	cache.clean()
	data = cache.get(DUMMY_URL)
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
	data = cache.get(DUMMY_URL)
	assert len(cache.cache.urls) == 1
	assert cache.cache.urls[0] == DUMMY_URL
def test_Get_Check_Return():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache = CacheForTests()
	data = cache.get(DUMMY_URL)
	assert len(data) == 2
	assert data[0]["val"] == 1
	assert data[1]["val"] == 1
def test_Get_return_hashes():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache.return_only_cache_files = True
	cache.clean()
	data = cache.get(DUMMY_URL)
	assert len(data) == 1
	assert data[0] == "70551c7a431274e4617c94ad307346d2.json"

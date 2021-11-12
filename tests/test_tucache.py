from pytrackunit.tucache import TuCache

DUMMY_URL = 'https://pokeapi.co/api/v2/pokemon/ditto'

def test_clean_start():
	cache = TuCache(_dir="pytest-web-cache")
	cache.clean()
def test_Get_Clean():
	cache = TuCache(_dir="pytest-web-cache")
	cache.clean()
	data = cache.get(DUMMY_URL)
	cache.clean()
def test_Get_WithFile():
	cache = TuCache(_dir="pytest-web-cache")
	cache.clean()
	data = cache.get(DUMMY_URL)
	assert data["abilities"][0]["ability"]["name"] == "limber"
	data = cache.get(DUMMY_URL)
	assert data["abilities"][0]["ability"]["name"] == "limber"
	cache.clean()
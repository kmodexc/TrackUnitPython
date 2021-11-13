from pytrackunit.tucache import TuCache

DUMMY_URL = 'https://pokeapi.co/api/v2/pokemon/ditto'
DATA_LEN = 21779

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
def test_Get_no_file_read():
	cache = TuCache(_dir="pytest-web-cache")
	cache.cache.dont_read_files = True
	cache.clean()
	data = cache.get(DUMMY_URL)
	assert data["abilities"][0]["ability"]["name"] == "limber"
	data = cache.get(DUMMY_URL)
	assert len(data) == 1
	assert data["list"] == []
	cache.clean()
def test_Get_verbose(capsys):
	cache = TuCache(_dir="pytest-web-cache",verbose=True)
	cache.clean()
	data = cache.get(DUMMY_URL)
	captured = capsys.readouterr()
	assert captured.out == DUMMY_URL+" "+str(DATA_LEN)+" W\n"
	data = cache.get(DUMMY_URL)
	captured = capsys.readouterr()
	assert captured.out == DUMMY_URL+" "+str(DATA_LEN)+" C\n"
	cache.clean()
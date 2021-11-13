from pytrackunit.webcache import WebCache, get_from_file
import os.path
import hashlib
from os import listdir
from os.path import isfile, join

DUMMY_URL = 'https://pokeapi.co/api/v2/pokemon/ditto'
DUMMY_RESPONSE_HASH = "3b28bef695a954335cadf285a6220b374bf5e947ef55102bea38823df53d2865"

def get_hash(x):
	return hashlib.sha256(x.encode('ascii')).hexdigest()
def test_Clean():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	assert os.path.exists(cache.dir)
	assert len(listdir(cache.dir)) == 0
	fname = os.path.join(cache.dir,"asdf.txt")
	f = open(fname,"w",encoding='utf8')
	f.write('{"data": "data"}')
	f.flush()
	f.close()
	cache.clean()
	assert os.path.exists(cache.dir)
	assert len(listdir(cache.dir)) == 0
	cache.clean()
	assert os.path.exists(cache.dir)
	assert len(listdir(cache.dir)) == 0
def test_GetFromFile_Clean():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	data = get_from_file('asdf')
	assert data is None
	cache.clean()
def test_GetFromFile_WithFile():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	fname = os.path.join(cache.dir,"asdf.txt")
	f = open(fname,"w",encoding='utf8')
	f.write('{"data": "data"}')
	f.flush()
	f.close()
	assert os.path.exists(fname)
	data = get_from_file(fname)
	assert data["data"] == "data"
	cache.clean()
def test_GetFromFile_With_incorrect_File():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	fname = os.path.join(cache.dir,"asdf.txt")
	f = open(fname,"w",encoding='utf8')
	f.write('{"data": "data"')
	f.flush()
	f.close()
	assert os.path.exists(fname)
	data = get_from_file(fname)
	assert data is None
	cache.clean()
def test_GetFromWeb():
	cache = WebCache(_dir="pytest-web-cache")
	data = cache.get_from_web(DUMMY_URL).text
	data_hash = get_hash(data)
	assert data_hash == DUMMY_RESPONSE_HASH
	cache.clean()
def test_Get_Clean():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	data = cache.get(DUMMY_URL)
	cache.clean()
def test_Get_WithFile():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	data = cache.get(DUMMY_URL)
	assert data["abilities"][0]["ability"]["name"] == "limber"
	data = cache.get(DUMMY_URL)
	assert data["abilities"][0]["ability"]["name"] == "limber"
	cache.clean()
def test_Get_no_file_read():
	cache = WebCache(_dir="pytest-web-cache")
	cache.dont_read_files = True
	cache.clean()
	data = cache.get(DUMMY_URL)
	assert data["abilities"][0]["ability"]["name"] == "limber"
	data = cache.get(DUMMY_URL)
	assert data == {}
	cache.clean()

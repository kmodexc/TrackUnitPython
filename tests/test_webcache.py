from pytrackunit.webcache import WebCache, get_from_file
import os.path
import hashlib
from os import listdir
from os.path import isfile, join
import asyncio

DUMMY_URL = 'https://pokeapi.co/api/v2/pokemon/ditto'
DUMMY_URL_HASH = "70551c7a431274e4617c94ad307346d2"

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
	data = asyncio.run(get_from_file('asdf'))
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
	data = asyncio.run(get_from_file(fname))
	assert data["data"] == "data"
	cache.clean()
def test_GetFromFile_With_incorrect_File():
	cache = WebCache(_dir="pytest-web-cache",verbose=True)
	cache.clean()
	fname = os.path.join(cache.dir,"asdf.txt")
	f = open(fname,"w",encoding='utf8')
	f.write('{"data": "data"')
	f.flush()
	f.close()
	assert os.path.exists(fname)
	data = asyncio.run(get_from_file(fname))
	assert data is None
def test_Get_Clean():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	data = asyncio.run(cache.get(DUMMY_URL))
	cache.clean()
def test_Get_WithFile():
	cache = WebCache(_dir="pytest-web-cache")
	cache.clean()
	data = asyncio.run(cache.get(DUMMY_URL))
	assert data["abilities"][0]["ability"]["name"] == "limber"
	data = asyncio.run(cache.get(DUMMY_URL))
	assert data["abilities"][0]["ability"]["name"] == "limber"
	cache.clean()
def test_Get_no_file_read():
	cache = WebCache(_dir="pytest-web-cache")
	cache.dont_read_files = True
	cache.clean()
	data = asyncio.run(cache.get(DUMMY_URL))
	assert data["abilities"][0]["ability"]["name"] == "limber"
	data = asyncio.run(cache.get(DUMMY_URL))
	assert data == {}
	cache.clean()
def test_Get_write_file():
	cache = WebCache(_dir="pytest-web-cache",verbose=True)
	fname = os.path.join(cache.dir,DUMMY_URL_HASH+".json")
	cache.clean()
	data = asyncio.run(cache.get(DUMMY_URL))
	data = asyncio.run(get_from_file(fname))
	assert data["abilities"][0]["ability"]["name"] == "limber"
def test_Get_verbose(capsys):
	cache = WebCache(_dir="pytest-web-cache",verbose=True)
	cache.clean()
	data = asyncio.run(cache.get(DUMMY_URL))
	captured = capsys.readouterr()
	assert captured.out.split(' ')[0] == DUMMY_URL
	assert captured.out.split(' ')[2] == "W\n"
	data = asyncio.run(cache.get(DUMMY_URL))
	captured = capsys.readouterr()
	assert captured.out.split(' ')[0] == DUMMY_URL
	assert captured.out.split(' ')[2] == "C\n"
def test_return_hashes():
	cache = WebCache(_dir="pytest-web-cache",verbose=True)
	cache.clean()
	cache.return_only_cache_files = True
	data = asyncio.run(cache.get(DUMMY_URL))
	assert data == DUMMY_URL_HASH+".json"

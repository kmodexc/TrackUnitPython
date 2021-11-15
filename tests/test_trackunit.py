from datetime import datetime
from pytrackunit.trackunit import TrackUnit

BASE_URL = "https://api.trackunit.com/public/Report/UnitExtendedInfo?Id=3331359"

class CacheForTests:
    """tucache class"""
    def __init__(self):
        self.urls = []
    def clean(self):
        pass
    def get(self,url):
        print(url)
        self.urls.append(url)
        retval = {}
        retval["list"] = []
        return retval

def test_get():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	tu.cache.clean()
	data = tu.get("Unit?id=3331359")
	assert len(data) == 1
	assert data[0]["serialNumber"] == "3603666"
	assert data[0]["name"] == "KT559-36 (416-36) WNK41636VKTKF0002"
def test_getunitlist():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	tu.cache.clean()
	data = tu.get_unitlist("WNK41636VKTKF0002")
	assert len(data) == 1
	assert data[0]["serialNumber"] == "3603666"
	assert data[0]["name"] == "KT559-36 (416-36) WNK41636VKTKF0002"
def test_gethistory():
	tu = TrackUnit()
	tu.cache.clean()
	tu.cache.dir = "pytest-web-cache"
	data = tu.get_history("3331359",tdelta=100)
	assert len(data) > 10000
def test_getcandata():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	tu.cache.clean()
	data = tu.get_candata("3331359",tdelta=100)
	assert len(data) > 10000
def test_getcandata_no_file_read():
	tu = TrackUnit()
	tu.cache.cache.dont_read_files = True
	tu.cache.dir = "pytest-web-cache"
	tu.cache.clean()
	data = tu.get_candata("3331359",tdelta=100)
	assert len(data) > 10000
	data = tu.get_candata("3331359",tdelta=100)
	assert len(data) == 0
	assert data == []
def test_getcandata_check_urls():
	tu = TrackUnit()
	tu.tdelta_end = datetime(2021,11,15,10,0,0,0)
	tu.cache = CacheForTests()
	tu.get_candata("3331359",tdelta=100)
	assert len(tu.cache.urls) == 4
	assert tu.cache.urls[0] == BASE_URL+"&from=2021-08-07T00:00:00.0000001Z&to=2021-09-06T00:00:00.0000000Z"
	assert tu.cache.urls[1] == BASE_URL+"&from=2021-09-06T00:00:00.0000001Z&to=2021-10-06T00:00:00.0000000Z"
	assert tu.cache.urls[2] == BASE_URL+"&from=2021-10-06T00:00:00.0000001Z&to=2021-11-05T00:00:00.0000000Z"
	assert tu.cache.urls[3] == BASE_URL+"&from=2021-11-05T00:00:00.0000001Z&to=2021-11-15T00:00:00.0000000Z"
	
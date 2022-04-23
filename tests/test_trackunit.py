import asyncio
from pytrackunit.trackunit import TrackUnit

VEH_ID = "3331359"

class CacheForTests:
    """tucache class"""
    def __init__(self):
        pass
    def clean(self):
        pass
    def generate_unit_list(self):
        for i in range(10):
            testobj = {}
            testobj['name'] = f"WNK{i}"
            testobj['serialNumber'] = "1234"
            yield testobj
        testobj = {}
        testobj['name'] = "KT559-36 (416-36) WNK41636VKTKF0002"
        testobj['serialNumber'] = "3603666"
        yield testobj 
    async def get_url(self, url):
        assert url == "Unit"
        return self.generate_unit_list()
    async def get_unitlist(self):
        return await self.get_url("Unit")
    async def generate_history_data(self):
        for i in range(10):
            testobj = {}
            testobj['time'] = 1
            testobj['value'] = i
            yield [testobj],testobj
    async def generate_can_data(self):
        for i in range(10):
            testobj = {}
            testobj['time'] = 1
            testobj['value'] = i
            yield [testobj],testobj
    async def generate_faults_data(self):
        for i in range(10):
            testobj = {}
            testobj['time'] = 1
            testobj['value'] = i
            yield [testobj],testobj
    def get_history(self,veh_id,tdelta,previter=None):
        #assert veh_id == VEH_ID
        return self.generate_history_data(), 10
    def get_candata(self,veh_id,tdelta=None,previter=None):
        #assert veh_id == VEH_ID
        return self.generate_can_data(), 10
    def get_faults(self,veh_id,tdelta=None,previter=None):
        #assert veh_id == VEH_ID
        return self.generate_faults_data(), 10

def test_getunitlist():
    tu = TrackUnit()
    #tu.cache.dir = "pytest-web-cache"
    tu.cache = CacheForTests()
    tu.cache.clean()
    data = tu.get_unitlist("WNK41636VKTKF0002")
    assert len(data) == 1
    assert data[0]["serialNumber"] == "3603666"
    assert data[0]["name"] == "KT559-36 (416-36) WNK41636VKTKF0002"
def test_gethistory():
    tu = TrackUnit()
    tu.cache = CacheForTests()
    tu.cache.clean()
    #tu.cache.dir = "pytest-web-cache"
    data = tu.get_history(VEH_ID,tdelta=1)
    assert len(data) == 10
def test_getcandata():
    tu = TrackUnit()
    tu.cache = CacheForTests()
    #tu.cache.dir = "pytest-web-cache"
    tu.cache.clean()
    data = tu.get_candata(VEH_ID,tdelta=1)
    assert len(data) == 10
def test_getfaults():
    tu = TrackUnit()
    tu.cache = CacheForTests()
    #tu.cache.dir = "pytest-web-cache"
    tu.cache.clean()
    data = tu.get_faults(VEH_ID,tdelta=100)
    assert len(data) == 10
def test_get_multi_history():
    tu = TrackUnit()
    tu.cache = CacheForTests()
    units = tu.get_unitlist()
    vids = list(map(lambda x: x['serialNumber'], units))
    tu.get_multi_history(vids,1000,f_process=None,progress_bar=False)
def test_get_multi_candata():
    tu = TrackUnit()
    tu.cache = CacheForTests()
    units = tu.get_unitlist()
    vids = list(map(lambda x: x['serialNumber'], units))
    tu.get_multi_candata(vids,1000,f_process=None,progress_bar=False)
def test_get_multi_faults():
    tu = TrackUnit()
    tu.cache = CacheForTests()
    units = tu.get_unitlist()
    vids = list(map(lambda x: x['serialNumber'], units))
    tu.get_multi_faults(vids,1000,f_process=None,progress_bar=False)

import os
import asyncio
from datetime import datetime
from pytrackunit.trackunit import TrackUnit

DB_PATH = "pytest_db.sqlite"
WEBCACHE_DIR = "pytest_webcache"
TDELTA_END = datetime(2022,3,1)

settings = {
    "use_async_generator": False,
    "verbose": True,
    "db_path":DB_PATH,
    "webcache_dir":WEBCACHE_DIR,
    "tdelta_end":TDELTA_END
}

def async_gen_to_list(gen):
    async def get_data(gen):
        data = []
        async for x, _id in gen:
            for y in x:
                data.append(y)
        print(data)
        return data
    return asyncio.run(get_data(gen))

def test_getunitlist():
    tu = TrackUnit(**settings)
    data = tu.get_unitlist("WNK41636VKTKF0002")
    assert len(data) == 1
    assert data[0]["serialNumber"] == "3603666"
    assert data[0]["name"] == "KT559-36 (416-36) WNK41636VKTKF0002"
    tu.cache.clean()
def test_gethistory():
    tu = TrackUnit(**settings)
    data = tu.get_history("3331359",tdelta=10)
    assert len(data) == 1759
    tu.cache.clean()
def test_getcandata():
    tu = TrackUnit(**settings)
    data = tu.get_candata("3331359",tdelta=1)
    assert len(data) == 1638
    tu.cache.clean()
def test_getfaults():
    tu = TrackUnit(**settings)
    data = tu.get_faults("3331359",tdelta=100)
    assert len(data) == 40
    tu.cache.clean()
def test_gethistory_sqlcache():
    if os.path.isfile(DB_PATH):
        os.remove(DB_PATH)
    tu = TrackUnit(**settings,tu_use_sqlcache=True)
    data = tu.get_history("3331359",tdelta=10)
    assert len(data) == 1759
def test_getcandata_sqlcache():
    if os.path.isfile(DB_PATH):
        os.remove(DB_PATH)
    tu = TrackUnit(**settings,tu_use_sqlcache=True)
    data = tu.get_candata("3331359",tdelta=1)
    assert len(data) == 1638
def test_getfaults_sqlcache():
    if os.path.isfile(DB_PATH):
        os.remove(DB_PATH)
    tu = TrackUnit(**settings,tu_use_sqlcache=True)
    data = tu.get_faults("3331359",tdelta=100)
    assert len(data) == 40
# def test_get_multi_history():
#     if os.path.isfile(DB_PATH):
#         os.remove(DB_PATH)
#     tu = TrackUnit(**settings,tu_use_sqlcache=True)
#     units = tu.get_unitlist()
#     vids = list(map(lambda x: x['id'], units))
#     tu_data = []
#     for x, _id in tu.get_multi_history(vids[15:20],1):
#         #print(x,_id)
#         tu_data.append(x)
#         assert False
#     tu_data = list(tu_data)
#     assert len(tu_data) == 1
# def test_get_multi_candata():
#     if os.path.isfile(DB_PATH):
#         os.remove(DB_PATH)
#     tu = TrackUnit(**settings,tu_use_sqlcache=True)
#     units = tu.get_unitlist()
#     vids = list(map(lambda x: x['id'], units))
#     tu_data = []
#     for x, _id in tu.get_multi_candata(vids[:5],1):
#         #print(x,_id)
#         assert False
#         tu_data.append(x)
#     tu_data = list(tu_data)
#     assert len(tu_data) == 1
# def test_get_multi_faults():
#     if os.path.isfile(DB_PATH):
#         os.remove(DB_PATH)
#     tu = TrackUnit(**settings,tu_use_sqlcache=True)
#     units = tu.get_unitlist()
#     vids = list(map(lambda x: x['id'], units))
#     tu_data = []
#     for x, _id in tu.get_multi_faults(vids[:5],100):
#         #print(x,_id)
#         assert False
#         tu_data.append(x)
#     tu_data = list(tu_data)
#     assert len(tu_data) == 1
    
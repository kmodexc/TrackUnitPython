from pytrackunit.trackunit import TrackUnit
def test_get():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	data = tu.get("Unit?id=3331359")
	assert len(data) == 1
	assert data[0]["serialNumber"] == "3603666"
	assert data[0]["name"] == "KT559-36 (416-36) WNK41636VKTKF0002"
def test_getunitlist():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	data = tu.get_unitlist("WNK41636VKTKF0002")
	assert len(data) == 1
	assert data[0]["serialNumber"] == "3603666"
	assert data[0]["name"] == "KT559-36 (416-36) WNK41636VKTKF0002"
def test_gethistory():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	data = tu.get_history("3331359",tdelta=100)
	assert len(data) > 10000
def test_getcandata():
	tu = TrackUnit()
	tu.cache.dir = "pytest-web-cache"
	data = tu.get_candata("3331359",tdelta=100)
	assert len(data) > 10000
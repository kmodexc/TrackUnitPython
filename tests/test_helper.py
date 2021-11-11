from pytrackunit.helper import *
def test_ma():
	testdata = []
	testobject = {}
	testobject["val"] = 2
	for i in range(10):
		testdata.append(testobject)
	moving_avg(testdata,"val")
def test_getsection():
	dobj = {}
	dobj['time'] = '2021-06-18T13:18:18.0000000Z'
	dobj['value'] = 2.0
	indata = 1000*[dobj]
	data = get_next_section(indata,lambda x: True)
	assert len(data) == len(indata)

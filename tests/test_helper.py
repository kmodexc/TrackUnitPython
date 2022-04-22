from pytrackunit.helper import *
def test_ma():
	testdata = []
	testobject = {}
	testobject["val"] = 2
	for i in range(10):
		testdata.append(testobject)
	moving_avg(testdata,"val")
def test_getsection_always_in_section():
	dobj = {}
	dobj['time'] = '2021-06-18T13:18:18.0000000Z'
	dobj['value'] = 2.0
	indata = 1000*[dobj]
	data = get_next_section(indata,lambda x: True)
	assert len(data) == len(indata)
def test_getsection_min_section_len():
	dobj = {}
	dobj['time'] = '2021-06-18T13:18:18.0000000Z'
	dobj['value'] = 2.0
	indata = 1000*[dobj]
	for i in range(len(indata)):
		indata[i]['value'] = i
	data = get_next_section(indata,lambda x: x['value'] % 2 == 0,fendsec=None,min_insec_len=2)
	assert data is None

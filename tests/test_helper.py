from pytrackunit.helper import *
def test_get_datetime():
	dt = get_datetime("2020-03-21T12:32:13.100000Z")
	assert dt.date().year == 2020
	assert dt.date().month == 3
	assert dt.date().day == 21
	assert dt.time().hour == 12
	assert dt.time().minute == 32
	assert dt.time().second == 13
	assert dt.time().microsecond == 100000 
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
def test_ma():
	testdata = []
	testobject = {}
	testobject["val"] = 2
	for i in range(10):
		testdata.append(testobject)
	moving_avg(testdata,"val")
def test_get_timediff_1():
	arg1 = "2020-03-21T12:32:13.100000Z"
	arg2 = "2020-03-21T12:32:13.200000Z"
	dt = get_time_diff(arg1,arg2)
	assert dt.days == 0
	assert dt.seconds == 0
	#assert dt.microseconds == 100000
def test_get_timediff_2():
	arg1 = "2020-03-21T12:32:14.100000Z"
	arg2 = "2020-03-21T12:32:13.100000Z"
	dt = get_time_diff(arg1,arg2)
	assert dt.days == 0
	assert dt.seconds == 1
	#assert dt.microseconds == 100000

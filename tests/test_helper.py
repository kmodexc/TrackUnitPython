import math
from copy import deepcopy
from pytrackunit.helper import *


END_UNIX_TS = datetime(year=2022,month=2,day=20,hour=10,second=10,microsecond=10000).timestamp()
END_UNIX_WITHOUT_TIME = datetime(year=2022,month=2,day=20).timestamp()
START_UNIX_TS = datetime(year=2022,month=2,day=10).timestamp()

# ------ get_datetime -------

def test_get_datetime():
	dt = get_datetime("2020-03-21T12:32:13.100000Z")
	assert dt.date().year == 2020
	assert dt.date().month == 3
	assert dt.date().day == 21
	assert dt.time().hour == 12
	assert dt.time().minute == 32
	assert dt.time().second == 13
	assert dt.time().microsecond == 100000 

# ------ get_next_section -------

def get_dataset(id=0):
	indata = None
	if id == 0:
		dobj = {}
		dobj['time'] = 0
		dobj['value'] = 2.0
		indata = []
		for i in range(10):
			dobj['time'] = datetime.fromtimestamp(END_UNIX_TS+i).isoformat()
			if (i // 3) % 2 == 0:
				dobj['value'] = 1
			else:
				dobj['value'] = -1
			indata.append(deepcopy(dobj))
	elif id == 1:
		dobj = {}
		dobj['time'] = 0
		dobj['value'] = 2.0
		indata = []
		for i in range(100):
			dobj['time'] = datetime.fromtimestamp(END_UNIX_TS+i).isoformat()
			dobj['value'] = math.sin(i/10)
			indata.append(deepcopy(dobj))
	elif id == 2:
		dobj = {}
		dobj['time'] = 0
		dobj['value'] = 2.0
		indata = []
		for i in range(10):
			dobj['time'] = datetime.fromtimestamp(END_UNIX_TS+i).isoformat()
			dobj['value'] = i % 4
			indata.append(deepcopy(dobj))
	return indata

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
	indata = []
	for i in range(1000):
		dobj['value'] = i
		indata.append(deepcopy(dobj))
	data = get_next_section(indata,lambda x: x['value'] % 2 == 0,fendsec=None,min_insec_len=2)
	assert data is None

def test_getsection_some_sequence_1():
	indata = get_dataset(1)
	data = get_next_section(indata,lambda x: x['value'] > 0,fendsec=None,min_insec_len=2)
	assert data is not None

def test_getsection_min_in_seg_1():
	indata = get_dataset(0)
	print(indata)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=None,
		min_insec_len=3,
		min_endsec_len=0)
	assert data is not None

def test_getsection_min_in_seg_2():
	indata = get_dataset(0)
	print(indata)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=None,
		min_insec_len=4,
		min_endsec_len=0)
	assert data is None

def test_getsection_min_end_seg_1():
	indata = get_dataset(0)
	print(indata)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= 0,
		min_insec_len=3,
		min_endsec_len=4)
	assert data is None

def test_getsection_min_end_seg_2():
	indata = get_dataset(0)
	print(indata)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= 0,
		min_insec_len=1,
		min_endsec_len=3)
	assert data is not None

def test_getsection_min_end_seg_3():
	indata = get_dataset(1)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= 0,
		min_insec_len=2,
		min_endsec_len=int(10*math.pi)-1)
	assert data is not None

def test_getsection_min_end_seg_3():
	indata = get_dataset(1)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= 0,
		min_insec_len=2,
		min_endsec_len=int(10*math.pi)+1)
	assert data is None

def test_getsection_end_seg_not_right():
	indata = get_dataset(1)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= -0.1,
		min_insec_len=2,
		min_endsec_len=int(10*math.pi)-2)
	assert data is None

def test_getsection_min_end_len_by_fendseg_1():
	indata = get_dataset(1)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= -0.1,
		min_insec_len=2,
		min_endsec_len=int(10*math.pi)-2)
	assert data is None

def test_getsection_min_end_len_by_fendseg_1():
	indata = get_dataset(2)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 0,
		fendsec=lambda x: x['value'] <= -0.1,
		min_insec_len=2,
		min_endsec_len=3)
	assert data is None

def test_getsection_min_end_len_by_fendseg_2():
	indata = get_dataset(2)
	data = get_next_section(
		indata,
		finsec=lambda x: x['value'] > 1,
		fendsec=lambda x: x['value'] < 1 ,
		min_insec_len=2,
		min_endsec_len=2)
	assert data is None

# ------ get_time_diff -------

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

# ------ moving_avg -------

def test_ma():
	testdata = []
	testobject = {}
	testobject["val"] = 2
	for i in range(10):
		testdata.append(testobject)
	moving_avg(testdata,"val")

def test_ma_insame():
	testdata = []
	testobject = {}
	testobject["val"] = 2
	for i in range(10):
		testdata.append(testobject)
	moving_avg(testdata,"val",in_same=True)

# ------ start_end_from_tdelta -------

def test_start_end_from_tdelta_timedelta():
	tdelta = timedelta(days=10)	
	start, end = start_end_from_tdelta(tdelta,preset_end=datetime.fromtimestamp(END_UNIX_TS))
	print(start, end)
	assert end.timestamp() == END_UNIX_WITHOUT_TIME
	assert start.timestamp() == START_UNIX_TS
def test_start_end_from_tdelta_int_days():
	tdelta = 10
	start, end = start_end_from_tdelta(tdelta,preset_end=datetime.fromtimestamp(END_UNIX_TS))
	print(start, end)
	assert end.timestamp() == END_UNIX_WITHOUT_TIME
	assert start.timestamp() == START_UNIX_TS
def test_start_end_from_tdelta_zero_days():
	tdelta = 0
	start, end = start_end_from_tdelta(tdelta,preset_end=datetime.fromtimestamp(END_UNIX_TS))
	print(start, end)
	assert end.timestamp() == END_UNIX_WITHOUT_TIME
	assert start.timestamp() == END_UNIX_WITHOUT_TIME

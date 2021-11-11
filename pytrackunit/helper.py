"""some additional helpers for trackunit"""

from datetime import datetime
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.dates

def plot_can_val(_data,valname):
    """plot value from getCanData"""
    data = filter(lambda x:x['name'] == valname,_data)
    plot_val(data,'value')

def get_datetime(time_string):
    """transforms trackunit time string to datetime"""
    return datetime.strptime(time_string.split('.')[0],"%Y-%m-%dT%H:%M:%S")

def plot_val(_data,valname):
    """plots a value from data (expected format from getHistory)"""
    data = list(set(map(lambda x: (x['time'],x[valname]),_data)))
    data = list(map(lambda x: (get_datetime(x[0]),float(x[1])),data))
    data.sort(key=lambda x: x[0])
    dates = matplotlib.dates.date2num(list(map(lambda x: x[0], data)))
    fig, _ax = plt.subplots()#marker='', linestyle='-'
    _ax.plot_date(dates, list(map(lambda x: x[1], data)),fmt=",-")
    _ax.locator_params(axis="y", nbins=10)
    fig.autofmt_xdate()
    plt.show()

def get_next_section(data,finsec,fendsec=None,min_insec_len=None,min_endsec_len=0):
    """
    returns the next section wich fulfills finsec with at least min_insec_len datapoints
    and ends with data wich fulfills fendsec which is at least min_endsec_len long
    """
    data.sort(key=lambda x: datetime.strptime(x['time'].split('.')[0],"%Y-%m-%dT%H:%M:%S"))
    out = []
    in_section = False
    off_sec_cnt = 0
    for datapoint in data:
        if not in_section and finsec(datapoint):
            out = []
            off_sec_cnt = 0
            out.append(datapoint)
            in_section = True
        elif in_section and finsec(datapoint):
            out.append(datapoint)
        elif in_section and not finsec(datapoint):
            if (min_insec_len is None or len(out) > min_insec_len) and \
                (fendsec is None or fendsec(datapoint)):
                if off_sec_cnt >= min_endsec_len:
                    return out
                off_sec_cnt += 1
                in_section = False
            else:
                in_section = False
                out = []
        elif not in_section and len(out) > 0:
            if fendsec(datapoint):
                off_sec_cnt += 1
                if off_sec_cnt >= min_endsec_len:
                    return out
            else:
                out = []
                off_sec_cnt = 0
    if (fendsec is None or min_endsec_len <= 0) and \
        (min_insec_len is None or len(out) >= min_insec_len):
        return out
    return None

def get_time_diff(timepoint_1,timepoint_2):
    """returns the diffrence between two trackunit timestrings"""
    dtt1 = datetime.strptime(timepoint_1.split('.')[0],"%Y-%m-%dT%H:%M:%S")
    dtt2 = datetime.strptime(timepoint_2.split('.')[0],"%Y-%m-%dT%H:%M:%S")
    return dtt1-dtt2

def moving_avg(data,valname,alpha=0.01,in_same = False):
    """
    creates a copy of data where the valname index has a moving avg with alpha applied
    """
    if in_same:
        data2 = data
    else:
        data2 = deepcopy(data)
    def fma(_x,last):
        return alpha*_x+(1-alpha)*last
    last = float(data[0][valname])
    for datapoint in data2:
        last = fma(float(datapoint[valname]),last)
        datapoint[valname] = str(last)
    return data2

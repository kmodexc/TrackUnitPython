import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates
from copy import deepcopy

def plot_can_val(_data,valname):
    data = filter(lambda x:x['name'] == valname,_data)
    plot_val(data,'value')

def plot_val(_data,valname):
    data = list(set(map(lambda x: (x['time'],x[valname]),_data)))
    data = list(map(lambda x: (datetime.strptime(x[0].split('.')[0],"%Y-%m-%dT%H:%M:%S"),float(x[1])),data))
    data.sort(key=lambda x: x[0])
    dates = matplotlib.dates.date2num(list(map(lambda x: x[0], data)))
    fig, ax = plt.subplots()#marker='', linestyle='-'
    ax.plot_date(dates, list(map(lambda x: x[1], data)),fmt=",-")
    ax.locator_params(axis="y", nbins=10)
    fig.autofmt_xdate()
    plt.show()

def get_next_section(data,finsec,fendsec=None,min_insec_len=None,min_endsec_len=0):
    data.sort(key=lambda x: datetime.strptime(x['time'].split('.')[0],"%Y-%m-%dT%H:%M:%S"))
    out = []
    in_section = False
    off_sec_cnt = 0
    for i in range(len(data)):
        if not in_section and finsec(data[i]):
            out = []
            off_sec_cnt = 0
            out.append(data[i])
            in_section = True
        elif in_section and finsec(data[i]):
            out.append(data[i])
        elif in_section and not finsec(data[i]):
            if (min_insec_len is None or len(out) > min_insec_len) and (fendsec is None or fendsec(data[i])):
                if off_sec_cnt >= min_endsec_len:
                    return out
                else:
                    off_sec_cnt += 1
                    in_section = False
            else:
                in_section = False
                out = []
        elif not in_section and len(out) > 0:
            if fendsec(data[i]):
                off_sec_cnt += 1
                if off_sec_cnt >= min_endsec_len:
                    return out
            else:
                out = []
                off_sec_cnt = 0
    return None

def get_time_diff(t1,t2):
    dtt1 = datetime.strptime(t1.split('.')[0],"%Y-%m-%dT%H:%M:%S")
    dtt2 = datetime.strptime(t2.split('.')[0],"%Y-%m-%dT%H:%M:%S")
    return (dtt1-dtt2)

def moving_avg(data,valname,alpha=0.01):
    data2 = deepcopy(data)
    def fma(x,last):
        return alpha*x+(1-alpha)*last
    last = float(data[0][valname])
    for i in range(len(data)):
        last = fma(data[i][valname],last)
        data2[i][valname] = str(last)
    return data2

def print_plot_info(data):
    dt0 = data[0]
    dtn = data[-1]
    print("Start: {} external: {} internal: {}".format(dt0['time'],dt0['externalPower'],dt0['batteryLevel']))
    print("Start: {} external: {} internal: {}".format(dtn['time'],dtn['externalPower'],dtn['batteryLevel']))
    print("Time difference: {}".format(get_time_diff(dtn['time'],dt0['time'])))
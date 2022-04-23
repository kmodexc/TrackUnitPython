# TrackUnitPython

![test](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/test.yml/badge.svg)
![lint](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/pylint.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/kmodexc/TrackUnitPython/badge.svg?branch=main)](https://coveralls.io/github/kmodexc/TrackUnitPython?branch=main)

Python API for Trackunit

## What is this package

This packages contains some usefull functions for an easy interface to TrackUnit's REST API. For information to the data see [here](https://dev.trackunit.com/docs).

Features:
- caches requests for faster access
- for timespan's bigger than 30 days it sufficiantly devides it into allowed requests
- processing big datasets more efficient by preprocessing per dataslice
- makes use of asyncio
- if data is cached it can process 12000 cached requests with 20 million data points in under 5 minutes.

For more features write an issue [here](https://github.com/einsteinmaster/TrackUnitPython/issues/new). Pull requests are welcome.

## How to use

### Install

Install the package via pip

``` sh
pip install pytrackunit
```

Create a file in your execution directory with the name `api.key` which contains your TrackUnit API token. If that doesnt work for you, you can set the token in the constructor by calling `tu = TrackUnit(api_key="<your key>")`.

### Example

``` python
from pytrackunit.helper import *
from pytrackunit.TrackUnit import TrackUnit

# Create the API
# It loads the key from api.key by default
tu = TrackUnit()

# Get all vehicles from trackunit
# This is executing the 'Unit' request 
vehicles = tu.get_unitlist()

# Get history is executing 'Report/UnitHistory'
# Gets the history for the last 100 days
history = tu.get_history(vehicles[0]['id'],100)

# Get extended data 'Report/UnitExtendedInfo'
# Gets the history for the last 100 days
data = tu.get_candata(vehicles[0]['id'],100)

# Get faults 'Report/UnitActiveFaults'
# Gets the history for the last 100 days
data = tu.get_faults(vehicles[0]['id'],100)

# The library supports processing multiple vehicles too
# For memory intensive requests it supports preprocessing requests
# Preprocessing is done with a function taking a list and a dict and returning a list.
# By default it prints a progress bar when using this function.
# Besides the data wich was returned by trackunit, process_slice gets some meta-
# data about the query which produced the _slice data.
units = ["123456","456789"]
def process_slice(_slice,meta):
    return list(map(lambda x: (meta["id"],x["time"],x["externalPower"]),_slice))
data = tu.get_multi_history( units, 365, process_slice)

```

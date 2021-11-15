# TrackUnitPython
Python API for Trackunit


![example workflow](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/test.yml/badge.svg)

![example workflow](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/pylint.yml/badge.svg)

![example workflow](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/python-publish.yml/badge.svg)

## What is this package

This packages contains some usefull functions for an easy interface to TrackUnit's REST API. For information to the data see [here](https://dev.trackunit.com/docs).

Features:
- caches requests for faster access
- for timespan's bigger than 30 days it sufficiantly devides it into allowd requests 

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
```

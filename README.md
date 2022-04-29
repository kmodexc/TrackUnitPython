# TrackUnitPython

![test](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/test.yml/badge.svg)
![lint](https://github.com/einsteinmaster/TrackUnitPython/actions/workflows/pylint.yml/badge.svg)
![Coverage Status](https://coveralls.io/repos/github/kmodexc/TrackUnitPython/badge.svg?branch=main)

Python API for Trackunit

## What is this package

This packages contains some usefull functions for an easy interface to TrackUnit's REST API. For information to the data see [here](https://dev.trackunit.com/docs).

Features:
- caches requests for faster access
- for timespan's bigger than 30 days it sufficiantly devides it into allowed requests
- asyncio functions availeble
- if data is cached it can process 12000 cached requests with 20 million data points in under 5 minutes.
- uses sqlite to cache data efficiently
- requests throttle function (Trackunit-API limits to 50 requests per second)
- provides stream-based generators for processing of big data

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
from pytrackunit.TrackUnit import TrackUnit

# Create the API
# It loads the key from api.key by default
tu = TrackUnit()
# alternatively
tu = TrackUnit(api_key="<api-key>")

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
# By default it prints a progress bar when using this function.
# Returns an iterator allowing processing big data
for x, _id in tu.get_multi_history( ['123456', '234567'] , 365):
    print(x, _id)
```

### Example async

``` python
import asyncio
from pytrackunit.TrackUnit import TrackUnit

async def main():
    # Create the API
    # It loads the key from api.key by default
    tu = TrackUnit(use_async_generator=True)

    # Get all vehicles from trackunit
    # This is executing the 'Unit' request 
    vehicles = await tu.async_get_unitlist()

    # Get history is executing 'Report/UnitHistory'
    # Gets the history for the last 100 days
    history = await tu.async_get_history('123456',100)

    # Get extended data 'Report/UnitExtendedInfo'
    # Gets the history for the last 100 days
    data = await tu.async_get_candata('123456',100)

    # Get faults 'Report/UnitActiveFaults'
    # Gets the history for the last 100 days
    data = await tu.async_get_faults('123456',100)

    # The library supports processing multiple vehicles too
    # For memory intensive requests it supports preprocessing requests
    # By default it prints a progress bar when using this function.
    # Returns an iterator allowing processing big data
    # This is prefered if data gets bigger, because it only collects data when needed,
    # thus reducing needed memory
    async for x, _id in tu.get_multi_history( ['123456', '234567'] , 365):
        print(x, _id)

if __name__ == '__main__':
    asyncio.run(main())
```

#!/usr/bin/python

import urllib2
import json
import shelve
import flights
import time

test_callsign = "VOZ482"
test_hex = "7C6D31"

def check_db(icao):
    history = shelve.open(".histfile")
    try:
        return history[icao]
    except:
        return None
    finally:
        history.close()

def store_db(icao, entry):
    history = shelve.open(".histfile")
    history[icao] = entry
    history.close()

def get_from_web(flightnum, icao):
    apiurl = "http://www.flightradar24.com/_json/planeInfoAndTrail_nocache.php?callsign=%s&hex=%s"
    response = urllib2.urlopen(apiurl % (flightnum, icao))
    planedata = response.read()

    d = json.loads(planedata)
    entry = {
        "rego": d["i"][4],
        "type": d["i"][5],
        "shorttype": d["i"][6],
            }
    store_db(icao, entry)
    flights.store_db(flightnum, d)
    time.sleep(2)
    return entry

def lookup(flightnum, icao):
    inf = check_db(icao)
    if ((flightnum != "" and flights.lookup(flightnum) is None) or inf is None):
        inf = get_from_web(flightnum, icao)
    return inf

if __name__ == "__main__":
    print lookup(test_callsign, test_hex)

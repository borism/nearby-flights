#!/usr/bin/env python

import csv
import math
import icao24
import flights
import airports
import os
import sys
import time

cardinals = [
     "N",
     "NNE",
     "NE",
     "ENE",
     "E",
     "ESE",
     "SE",
     "SSE",
     "S",
     "SSW",
     "SW",
     "WSW",
     "W",
     "WNW",
     "NW",
     "NNW"]

def friendlyangle(angle):
    return cardinals[int(round((angle % 360) / 22.5) % len(cardinals))]

def distance(origin, dest):
    lat1, lon1 = origin
    lat2, lon2 = dest
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    d = math.acos(math.sin(math.radians(lat1)) *
            math.sin(math.radians(lat2)) +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) * math.cos(dlon))

    if math.sin(dlon) < 0:
        tc1 = math.acos((math.sin(math.radians(lat2)) -
                math.sin(math.radians(lat1))*math.cos(d)) /
                (math.sin(d)*math.cos(math.radians(lat1))))
    else:
        tc1 = 2 * math.pi - math.acos((math.sin(math.radians(lat2)) -
                math.sin(math.radians(lat1))*math.cos(d)) /
                (math.sin(d)*math.cos(math.radians(lat1))))

    return d * 6371, 360 - math.degrees(tc1)

timenow = time.mktime(time.localtime())
timelast = os.path.getmtime("raw.csv")

if (timenow - timelast > 45):
    os.system('rm -f raw.csv data.xml')
    os.system('wget --quiet "http://www.flightradar24.com/_xml/plane_data3.php" -O data.xml')
    os.system('echo "hex,code,flight,alt,lat,long,a,b,c,d,date" > raw.csv')
    os.system('tidy -quiet -xml data.xml | grep newpoly | cut -c26- | cut -f-11 -d "," >> raw.csv')

d = csv.DictReader(open("raw.csv"), delimiter=",")
planes = []
me = [-33.887945, 151.159258]

for row in d:
    dist, bearing = distance(me, [float(row["lat"]), float(row["long"])])
    row['dist'] = dist
    row['bearing'] = bearing
    if (int(row['alt']) <= 0): continue
    planes.append(row)

planes = sorted(planes, key=lambda item: item['dist'])

for i in range(0,7):
    print "%s %2.2f km    %s %d" % (planes[i]['flight'],
                           planes[i]['dist'],
                           friendlyangle(planes[i]['bearing']),
                           planes[i]['bearing'])

    plinfo = icao24.lookup(planes[i]['flight'], planes[i]['hex'])
    if (plinfo):
        print plinfo["rego"], plinfo["type"], plinfo["shorttype"]
    try:
        flinfo = flights.lookup(planes[i]['flight'])
        if (flinfo):
            origin = flinfo["from"]
            destination = flinfo["to"]
            print "From: %s %s" % (origin, airports.lookup(origin))
            print "To:   %s %s" % (destination, airports.lookup(destination))
    except KeyError:
        print "No origin / destination information"
    print

#!/usr/bin/env python
import csv, math, icao24, flights, airports, os, sys, time, datetime, getopt

r = 0
planes = []
format = "%Y-%m-%d %H:%M:%S"

opts, args = getopt.getopt(sys.argv[1:], 'l:L:r:')
for opt, arg in opts:
    if opt == '-l':
        lat = float(arg)
    elif opt == '-L':
        lon = float(arg)
    elif opt == '-r':
        r = int(arg)

if lat and lon:
    me = [lat, lon]
else:
    print "please provide both latitude and longtitude"
    sys.exit(1)

if r <= 0:
    r = 500

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
if os.path.exists("raw.csv"):
 timelast = os.path.getmtime("raw.csv")
else:
 timelast = 0
if (timenow - timelast > 45):
    os.unlink('raw.csv')
    os.unlink('data.xml')
    os.system('wget --quiet "http://www.flightradar24.com/_xml/plane_data3.php" -O data.xml')
    os.system('echo "hex,code,flight,alt,lat,long,a,b,c,d,date" > raw.csv')
    os.system('tidy -quiet -xml data.xml | grep newpoly | cut -c26- | cut -f-11 -d "," >> raw.csv')
    os.system('cp raw.csv raw.csv.`date +%Y.%m.%d-%H:%M`')

d = csv.DictReader(open("raw.csv"), delimiter=",")

try:
 for row in d:
    dist, bearing = distance(me, [float(row["lat"]), float(row["long"])])
    row['dist'] = dist
    row['bearing'] = bearing
    if (int(row['alt']) <= 0): continue
    planes.append(row)
except:
 sys.exit(0)

planes = sorted(planes, key=lambda item: item['dist'])

if not planes:
 sys.exit(1)

for i in range(0,len(planes)):
    if (planes[i]['dist'] > r):
     break
    heading = abs(int(planes[i]['bearing']) - int(planes[i]['b']))
    speed = int(planes[i]['a'])*1.852
    try:
     eta = str("%d" % ((int(planes[i]['dist'])*60)/speed)) + "m"
    except ZeroDivisionError:
     eta = "-"
    if (heading < 170) or (heading > 190):
     eta = "-"
    if planes[i]['flight']:
     flt = str(planes[i]['flight'])
    else:
     flt = "      "
    ident = flt +"\t"+ str(planes[i]['alt']) +"ft\t"+ str("%.1f" % planes[i]['dist']) +"km\t"+ str("%03.0f" % float(planes[i]['bearing'])) +" "+ friendlyangle(planes[i]['bearing']) +"\t"+ str("%03.0f" % float(planes[i]['b'])) +"\t"+ str("%3.0f" % speed) +"kph\tETA "+ eta +"\t"
    plinfo = icao24.lookup(planes[i]['flight'], planes[i]['hex'])
    if (plinfo):
        print datetime.datetime.today().strftime(format), ident, plinfo["rego"], "\t", plinfo["shorttype"], "\t",
    try:
        flinfo = flights.lookup(planes[i]['flight'])
        if (flinfo):
            origin = flinfo["from"]
            destination = flinfo["to"]
            print "%s-%s\t\tFrom %s to %s" % (origin, destination, airports.lookup(origin), airports.lookup(destination))
        else:
            print "-"
    except KeyError:
        print "-"

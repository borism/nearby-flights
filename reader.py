#!/usr/bin/env python
import csv, math, icao24, flights, airports, os, sys, time, datetime, getopt, shutil, urllib2, distbear

h = 0
r = 0
hrzn = False
fx = False
planes = []
fixes = []
format = "%Y-%m-%d %H:%M:%S"

opts, args = getopt.getopt(sys.argv[1:], 'l:L:r:h:HF')
for opt, arg in opts:
    if opt == '-l':
        lat = float(arg)
    elif opt == '-L':
        lon = float(arg)
    elif opt == '-h':
        h = float(arg)
    elif opt == '-r':
        r = int(arg)
    elif opt == '-H':
        hrzn = True
    elif opt == '-F':
        fx = True

if lat and lon:
    me = [lat, lon]
else:
    print "please provide both latitude and longtitude"
    sys.exit(1)

if h < 0:
    h = 0 
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

timenow = time.mktime(time.localtime())
if os.path.exists("raw.csv"):
    timelast = os.path.getmtime("raw.csv")
else:
    timelast = 0
if (timenow - timelast > 45):
    #os.unlink('data.xml')
    #dataout = open("data.xml", "w")
    data = urllib2.urlopen("http://www.flightradar24.com/_xml/plane_data3.php").read()
    #print >> dataout, data
    #dataout.close()

    if os.path.exists('raw.csv'):
        os.unlink('raw.csv')
    rawout = open("raw.csv", "w")
    print >> rawout, "hex,code,flight,alt,lat,long,a,b,c,d,date"
    for dat in data.splitlines():
        da = dat.split('\"')
        try:
            print >> rawout, da[1].split(' ')[2], da[1].split(' ')[3].rstrip(',')
        except IndexError:
            continue
    rawout.close()

    #os.system('tidy -quiet -xml data.xml | grep newpoly | cut -c26- | cut -f-11 -d "," >> raw.csv.tidy')

    rawdest = "raw.csv." + datetime.datetime.today().strftime("%Y.%m.%d-%H:%M")
    shutil.copyfile("raw.csv", rawdest)

d = csv.DictReader(open("raw.csv"), delimiter=",")

try:
    for row in d:
        dist, bearing = distbear.distance(me, [float(row["lat"]), float(row["long"])])
        row['dist'] = dist
        row['bearing'] = bearing
        if (int(row['alt']) <= 0): continue
        planes.append(row)
except:
    print "no flights found"
    sys.exit(1)

planes = sorted(planes, key=lambda item: item['dist'])

fixcsv = "fix.csv." + str("%d" % me[0]) +"."+ str("%d" % me[1])
if fx and not os.path.exists(fixcsv):
    f = csv.DictReader(open("fix.csv"), delimiter=",")
    for fix_row in f:
        fix_dist, fix_bearing = distbear.distance([float("%d" % me[0]), float("%d" % me[1])], [float(fix_row["lat"]), float(fix_row["lon"])])
        fix_row['dist'] = fix_dist
        fixes.append(fix_row)

    fixes = sorted(fixes, key=lambda item: item['dist'])

    fixout = open(fixcsv, "w")
    print >> fixout, "fix,lat,lon"
    for j in range(0,len(fixes)):
        if (int(fixes[j]['dist']) > 1000):
            fixout.close()
            fixes = []
            break
        else:
            fixoutstr = str(fixes[j]['fix']) +","+ str(fixes[j]['lat']) +","+ str(fixes[j]['lon'])
            print >> fixout, fixoutstr

for i in range(0,len(planes)):
    if (planes[i]['dist'] > r):
        break

    if fx:
        f = csv.DictReader(open(fixcsv), delimiter=",")    
        for fix_row in f:
            fix_dist, fix_bearing = distbear.distance([float(planes[i]['lat']), float(planes[i]['long'])], [float(fix_row["lat"]), float(fix_row["lon"])])
            fix_row['dist'] = fix_dist
            fix_row['bearing'] = fix_bearing
            fixes.append(fix_row)

        fixes = sorted(fixes, key=lambda item: item['dist'])

        for j in range(0,len(fixes)):
            if (int(fixes[j]['bearing']) == int(planes[i]['b'])):
                fixstr = "\t" + str(fixes[j]['fix']) + "\t"
                break
            else:
                if (int(fixes[j]['dist']) > 500):
                    fixstr = "\t  -  \t"
                    break
                else:
                    continue

        fixes = []
    else:
        fixstr = "\t"

    heading = abs(int(planes[i]['bearing']) - int(planes[i]['b']))
    v = float(planes[i]['a'])*1.852
    speed = str("%3.0f" % v)

    if (v > 0) and (heading > 157) and (heading < 203):
        eta = str("%d" % ((int(planes[i]['dist'])*60)/v)) + "m"
    else:
        eta = "-"

    if planes[i]['flight']:
        flt = str(planes[i]['flight'])
    else:
        flt = "      "

    alt = str("%05.0f" % float(planes[i]['alt']))
    alt_m = float(planes[i]['alt']) * 0.3048
    dist = str("%03.1f" % float(planes[i]['dist']))
    bearing = str("%03.0f" % float(planes[i]['bearing']))
    bearing_f = friendlyangle(planes[i]['bearing'])
    heading = str("%03.0f" % float(planes[i]['b']))

    if hrzn:
        horizon_d = 3.57 * (math.sqrt(alt_m) + math.sqrt(h))
        if planes[i]['dist'] < horizon_d:
            horizon = "_-_"
        else:
            horizon = "___"
        ident = flt +"\t"+ alt +"ft\t"+ dist +"km\t"+ horizon +"\t"+ bearing +" "+ bearing_f +"\t"+ heading + fixstr + speed +"kph\tETA "+ eta +"\t"
    else:
        ident = flt +"\t"+ alt +"ft\t"+ dist +"km\t"+ bearing +" "+ bearing_f +"\t"+ heading + fixstr + speed +"kph\tETA "+ eta +"\t"

    plinfo = icao24.lookup(planes[i]['flight'], planes[i]['hex'])
    if (plinfo):
        print datetime.datetime.today().strftime(format), ident, plinfo["rego"], "\t", plinfo["shorttype"],
    
    try:
        flinfo = flights.lookup(planes[i]['flight'])
        if (flinfo):
            origin = flinfo["from"]
            destination = flinfo["to"]
            print "\t%s-%s\t\tFrom %s to %s" % (origin, destination, airports.lookup(origin), airports.lookup(destination))
        else:
            print "   -   "
    except KeyError:
        print "   -   "

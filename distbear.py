#!/usr/bin/env python
import math, sys

def distance(origin, dest):
    tc1 = 1
    lat1, lon1 = origin
    lat2, lon2 = dest
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    d = math.acos(math.sin(math.radians(lat1)) *
            math.sin(math.radians(lat2)) +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) * math.cos(dlon))

    if math.sin(dlon) < 0 and (math.sin(d)*math.cos(math.radians(lat1))) != 0:
        tc1 = math.acos(float("%.10f" % ((math.sin(math.radians(lat2)) -
                math.sin(math.radians(lat1))*math.cos(d)) /
                (math.sin(d)*math.cos(math.radians(lat1))))))
    elif (math.sin(d)*math.cos(math.radians(lat1))) != 0:
        tc1 = 2 * math.pi - math.acos(float("%.10f" % ((math.sin(math.radians(lat2)) -
                math.sin(math.radians(lat1))*math.cos(d)) /
                (math.sin(d)*math.cos(math.radians(lat1))))))

    return d * 6371, 360 - math.degrees(tc1)

if __name__ == "__main__":
    for p in sys.stdin:
        co = p.split(' ')
        print "%d %s %s" % ((distance([float(co[0]),float(co[1])],[float(co[2]),float(co[3])])[0] * 1000), co[4], co[5].rstrip('\n'))

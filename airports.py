#!/usr/bin/python

import csv

def lookup(code):
    if (not code): return None
    return data[code]

d = open("iata-airport-codes.txt")
data = {}

for row in d:
    line = row.strip()
    code = line[:3]
    airport = line[4:]
    data[code] = airport

d.close()

if __name__ == "__main__":
    import sys
    print lookup(sys.argv[1])

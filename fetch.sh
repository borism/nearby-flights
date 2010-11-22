#!/bin/sh

set -e

rm -f raw.csv data.xml

wget "http://www.flightradar24.com/_xml/plane_data3.php" -O data.xml
echo "hex,code,flight,alt,lat,long,a,b,c,d,date" > raw.csv
tidy -xml data.xml | grep newpoly | cut -c26- | cut -f-11 -d "," >> raw.csv

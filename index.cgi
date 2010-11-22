#!/usr/bin/python

import cgi
import csv
import os

def main():
    print "Content-type: text/html\n"
    print "<html><body><h1>Nearby Flights</h1><pre>"
    import reader
    print "</pre></body></html>"

main()

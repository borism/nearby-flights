#!/usr/bin/env python

import shelve
import sgmllib
import sys

class InfoParser(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)

    def parse(self, some_html):
        self.ret = {}
        self.state = 0
        self.nexttoken = ""
        self.feed(some_html)
        self.close()
        return self.ret

    def handle_data(self, data):
        if (data[:4] == "From"):
            self.state = 1
            self.nexttoken = "from"
            return
        if (data[:2] == "To"):
            self.state = 1
            self.nexttoken = "to"
            return
        if (data[:7] == "Airline"):
            self.state = 2
            self.nexttoken = "airline"
            return
        if (self.state == 1):
            self.state = 2
            return
        if (self.state == 2):
            self.ret[self.nexttoken] = data.strip()
            self.state = 0
            self.nexttoken = ""

def parse(e):
    inf = InfoParser()
    a = {}
    a.update(inf.parse(e["i"][7]))
    a.update(inf.parse(e["i"][15]))
    return a

def store_db(flightnum, entry):
    history = shelve.open("flights.db")
    if (flightnum != ""):
        history[flightnum] = parse(entry)
    history.close()

def lookup(flightnum):
    history = shelve.open("flights.db")
    if (flightnum == ""): return None
    try:
        return history[flightnum]
    except:
        return None
    finally:
        history.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print lookup(sys.argv[1])
    else:
        history = shelve.open("flights.db")
        for i in history:
            print i, history[i]
        history.close()

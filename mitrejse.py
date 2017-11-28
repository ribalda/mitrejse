#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Ricardo Ribalda"
__copyright__ = "Copyright 2017, Ricardo Ribalda"
__license__ = "GPL"

import web
import requests
from xml.dom import minidom
import datetime
from dateutil import parser

urls = (
    '/', 'index',
    '/(station)', 'station',
)
render = web.template.render('templates/', base='layout')

# Values obtained using:
# https://epsg.io/map#srs=4326&x=12.504158&y=55.667069&z=16 (WGS84)
# and:
# http://xmlopen.rejseplanen.dk/bin/rest.exe/stopsNearby?coordX=55673059&coordY=12565557
stations = {
    "Home": {
        "req": "id=1402",
        "dir": u"Ny Ellebjerg St."
    },
    "Ryparken": {
        "req": "id=52547",
        "dir": u"Østerbro, Ryparken"
    },
    "Work C": {
        "req": "id=8600701",
        "dir": u"Ballerup St."
    },
    "Work F": {
        "req": "id=8600742",
        "dir": u"Hellerup St."
    },
}

baseurl = "http://xmlopen.rejseplanen.dk/bin/rest.exe/departureBoard?"


class index:
    def GET(self, name=None):
        return render.index(stations.keys())


class station:

    def parseDeparture(self, station, dep):
        if dep.attributes['direction'].value != station["dir"]:
            return None
        if dep.hasAttribute("rtTime"):
            time = dep.attributes['rtTime'].value
        else:
            time = dep.attributes['time'].value
        time = dep.attributes['date'].value + " " + time
        time = parser.parse(time)
        now = datetime.datetime.now()

        if (now > time):
            difftime = now - time
        else:
            difftime = time - now
        difftime = difftime.seconds

        d = dict()
        d["name"] = dep.attributes['name'].value
        d["dir"] = station["dir"]
        d["minutes"] = int(round(abs(difftime) / 60.0))
        d["lost"] = now > time
        d["rt"] = dep.hasAttribute("rtTime")
        return d

    def GET(self, name=None):
        station = stations[web.input().name]
        response = requests.post(baseurl + station["req"])
        xmldoc = minidom.parseString(response.content)
        itemlist = xmldoc.getElementsByTagName('Departure')
        deps = list()
        for i in itemlist:
            d = self.parseDeparture(station, i)
            if d is None:
                continue
            deps.append(d)
        # print(deps)
        return render.station(deps)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

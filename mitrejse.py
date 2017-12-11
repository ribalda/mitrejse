#!/usr/bin/python3
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
renderesp = web.template.render('templates')

# Values obtained using:
# https://epsg.io/map#srs=4326&x=12.504158&y=55.667069&z=16 (WGS84)
# and:
# http://xmlopen.rejseplanen.dk/bin/rest.exe/stopsNearby?coordX=55673059&coordY=12565557
stations = {
    "Home": {
        "req": "id=1402",
        "dir": (u"Ny Ellebjerg St.", u"Sjælør St.", u"Mozarts Plads")
    },
    "Ryparken": {
        "req": "id=52547",
        "dir": (u"Østerbro, Ryparken")
    },
    "Work C": {
        "req": "id=8600701",
        "dir": (u"Ballerup St.", u"Frederikssund St.")
    },
    "Work F": {
        "req": "id=8600742",
        "dir": (u"Hellerup St.", u"Klampenborg St.")
    },
    "Flintholm": {
        "req": "id=8600736?id=8600736&useBus=0&useMetro=0",
        "dir": (u"Klampenborg St.")
    },
}

baseurl = "http://xmlopen.rejseplanen.dk/bin/rest.exe/departureBoard?"


class index:
    def GET(self, name=None):
        return render.index(stations.keys())


class station:

    def parseDeparture(self, station, dep):
        if not dep.attributes['direction'].value in station["dir"]:
            return None
        if dep.hasAttribute("rtTime"):
            time = dep.attributes['rtTime'].value
        else:
            time = dep.attributes['time'].value
        time = dep.attributes['date'].value + " " + time
        time = parser.parse(time, dayfirst=True)
        now = datetime.datetime.now()

        if (now > time):
            difftime = now - time
        else:
            difftime = time - now
        difftime = difftime.seconds

        d = dict()
        d["name"] = dep.attributes['name'].value
        d["dir"] = dep.attributes['direction'].value
        d["minutes"] = int(round(abs(difftime) / 60.0))
        d["lost"] = now > time
        d["rt"] = dep.hasAttribute("rtTime")
        return d

    def GET(self, name=None):
        station = stations[web.input().name]
        esp = hasattr(web.input(), 'esp')
        response = requests.post(baseurl + station["req"])
        xmldoc = minidom.parseString(response.content)
        itemlist = xmldoc.getElementsByTagName('Departure')
        deps = list()
        for i in itemlist:
            d = self.parseDeparture(station, i)
            if d is None:
                continue
            deps.append(d)
            if (esp):
                break
        # print(deps)
        if (esp):
            return renderesp.esp(deps)
        else:
            return render.station(deps)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

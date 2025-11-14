#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Ricardo Ribalda"
__copyright__ = "Copyright 2017, Ricardo Ribalda"
__license__ = "GPL"

import requests
from xml.dom import minidom
import datetime
from dateutil import parser
from dateutil.tz import gettz

from flask import Flask, render_template, request


urls = (
    '/', 'index',
    '/(station)', 'station',
)

# Values obtained using:
# https://epsg.io/map#srs=4326&x=12.504158&y=55.667069&z=16 (WGS84)
# and:
# http://xmlopen.rejseplanen.dk/bin/rest.exe/stopsNearby?coordX=55673059&coordY=12565557
stations = {
    "Home": {
        "req": "id=1402",
        "dir": (u"Ny Ellebjerg St.", u"Sjælør St.", u"Mozarts Plads", u"Teglholmen", u"Nørreport St.")
    },
    "Ryparken": {
        "req": "id=1404",
        "dir": (u"Østerbro, Ryparken")
    },
    "Work C": {
        "req": "id=8600701",
        "dir": (u"Ballerup St.", u"Frederikssund St.", u"Ølstykke St.")
    },
    "Work F": {
        "req": "id=8600742",
        "dir": (u"Hellerup St.", u"Klampenborg St.")
    },
    "Flintholm": {
        "req": "id=8600736&useBus=0&useMetro=0",
        "dir": (u"Klampenborg St.")
    },
}

baseurl = "http://xmlopen.rejseplanen.dk/bin/rest.exe/departureBoard?"


def parseDeparture(station, dep):
    if not dep.attributes['direction'].value in station["dir"]:
        return None
    if dep.hasAttribute("rtTime"):
        time = dep.attributes['rtTime'].value
    else:
        time = dep.attributes['time'].value
    time = dep.attributes['date'].value + " " + time + " KKT"
    time = parser.parse(time, dayfirst=True, tzinfos={"KKT": gettz("Europe/Copenhagen")})
    now = datetime.datetime.now(datetime.timezone.utc)

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

def getDepartures(station):
    response = requests.post(baseurl + station["req"])
    xmldoc = minidom.parseString(response.content)
    itemlist = xmldoc.getElementsByTagName('Departure')
    deps = list()
    for i in itemlist:
        d = parseDeparture(station, i)
        if d is None:
            continue
        deps.append(d)
    return deps

app = Flask(__name__)


@app.route('/')
def index():
    return render_template(
        'index.html',
        stations=stations.keys(),
        title="Index")


@app.route('/station')
def station():
    station = stations[request.args.get('name')]
    deps = getDepartures(station)
    return render_template('station.html', transport=deps, title="Station")

if __name__ == "__main__":
    app.run (host="0.0.0.0", port=8080, debug=True)

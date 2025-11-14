#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Ricardo Ribalda"
__copyright__ = "Copyright 2017, Ricardo Ribalda"
__license__ = "GPL"

import requests
import datetime
from dateutil import parser
from dateutil.tz import gettz
from urllib.parse import quote
import google.auth
from google.cloud import secretmanager

from flask import Flask, render_template, request


def get_secret(secret_name="REJSEPLANEN_API_KEY"):

    _, project_id = google.auth.default()

    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_name, "latest")
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


# Values obtained using:
# https://www.gps-coordinates.net/
# www.rejseplanen.dk/api/location.nearbystops?accessId=API_KEY&format=json&lang=en&originCoordLat=55.71531535480527&originCoordLong=12.558932313943863
# www.rejseplanen.dk/api/departureBoard?accessId=API_KEY&format=json&lang=en&duration=120&id=A%3D1%40O%3DRyparken%20St.%20%28togbus%29%40X%3D12558856%40Y%3D55715403%40U%3D86%40L%3D8650644%40'
stations = {
    "Home": {
        "id": "A=1@O=Gartnerivej (Ryparken)@X=12559387@Y=55720553@U=86@L=1402@",
        "line": "14",
        "directionFlag": "2",
    },
    "Ryparken": {
        "id": "A=1@O=Ryparken St. (togbus)@X=12558856@Y=55715403@U=86@L=8650644@",
        "line": "14",
        "directionFlag": "1",
    },
}

baseurl = f"https://www.rejseplanen.dk/api/"


def parseDeparture(dep):
    out = dict()
    out["dir"] = dep["direction"]
    out["directionFlag"] = dep["directionFlag"]
    out["name"] = dep["name"]

    # Get time
    if "rtTime" in dep:
        time = dep["rtTime"]
    else:
        time = dep["time"]
    time = parser.parse(
        f"{dep['date']} {time} KKT",
        dayfirst=True,
        tzinfos={"KKT": gettz("Europe/Copenhagen")},
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    difftime = abs((now - time).total_seconds())
    out["minutes"] = int(round(abs(difftime) / 60.0))
    out["lost"] = now > time
    out["rt"] = "prognosisType" in dep

    return out


def getDepartures(station):
    url = f"{baseurl}departureBoard?accessId={get_secret()}&format=json&lang=en&duration=120&id={quote(station['id'])}&lines={station['line']}"
    response = requests.post(url).json()

    departures = tuple(map(parseDeparture, response["Departure"]))

    return [d for d in departures if d["directionFlag"] == station["directionFlag"]]


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", stations=stations.keys(), title="Index")


@app.route("/station")
def station():
    station = stations[request.args.get("name")]
    deps = getDepartures(station)
    return render_template("station.html", transport=deps, title="Station")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

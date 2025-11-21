#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Ricardo Ribalda"
__copyright__ = "Copyright 2017, Ricardo Ribalda"
__license__ = "GPL"

import requests
import datetime
import logging
import os
from dateutil import parser
from dateutil.tz import gettz
from urllib.parse import quote
import google.auth
from google.cloud import secretmanager

from flask import Flask, render_template, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_NAME = "REJSEPLANEN_API_KEY"


def get_secret():
    if os.environ.get(SECRET_NAME):
        return os.environ.get(SECRET_NAME)
    try:
        _, project_id = google.auth.default()
        if not project_id:
            logger.error("No Google Cloud project ID found.")
            return None

        client = secretmanager.SecretManagerServiceClient()
        name = client.secret_version_path(project_id, SECRET_NAME, "latest")
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to retrieve secret {SECRET_NAME}: {e}")
        return None


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
    out["dir"] = dep.get("direction", "Unknown")
    out["directionFlag"] = dep.get("directionFlag", "InvalidDirectionFlag")
    out["name"] = dep.get("name", "Unknown")

    time = dep.get("rtTime", dep.get("time", "InvalidTime"))
    try:
        time = parser.parse(
            f"{dep['date']} {time} KKT",
            dayfirst=True,
            tzinfos={"KKT": gettz("Europe/Copenhagen")},
        )
        now = datetime.datetime.now(datetime.timezone.utc)
        departure_time = time.astimezone(datetime.timezone.utc)
        delta = departure_time - now
        out["minutes"] = int(delta.total_seconds() / 60)
        out["lost"] = delta.total_seconds() < 0
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing date/time: {e}")
        out["minutes"] = 0
        out["lost"] = True

    out["rt"] = "prognosisType" in dep

    return out


def getDepartures(station):
    api_key = get_secret()
    if not api_key:
        logger.error("No API key available.")
        return []

    url = f"{baseurl}departureBoard?accessId={api_key}&format=json&lang=en&duration=120&id={quote(station['id'])}&lines={station['line']}"

    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        departures = tuple(map(parseDeparture, data["Departure"]))

        return [d for d in departures if d["directionFlag"] == station["directionFlag"]]
    except Exception as e:
        logger.error(f"Error fetching departures: {e}")
        return []


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", stations=stations.keys(), title="Index")


@app.route("/station")
def station():
    station_name = request.args.get("name")
    if not station_name or station_name not in stations:
        return render_template(
            "index.html", stations=stations.keys(), title="Station Not Found"
        )

    station_config = stations[station_name]
    deps = getDepartures(station_config)
    return render_template("station.html", transport=deps, title=station_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

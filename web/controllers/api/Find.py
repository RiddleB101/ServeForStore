# -*- coding: utf-8 -*-

from web.controllers.api import route_api
from common.libs.Helper import getCurrentDate
from common.models.beacon.BeaconInfo import BeaconInfo
from application import app, db
from flask import request, json, jsonify


@route_api.route("/find/beacon", methods=['GET', 'POST'])
def Beacon():
    resp = {"code": 200, "data": {}}
    req = request.values
    beacon_info = req['beacon_info'] if 'beacon_info' in req else ''
    beacons = []
    for i in beacon_info:
        beacons.append(json.dumps(i))
    for beacon in beacons:
        beacon_uuid = BeaconInfo.query.filter_by(uuid=beacon.uuid).first()
        if beacon_uuid and beacon.accuracy <= 20:
            target = BeaconInfo()


    return jsonify(resp)

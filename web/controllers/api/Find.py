# -*- coding: utf-8 -*-

from web.controllers.api import route_api
from common.libs.Helper import getCurrentDate
from application import app, db
from flask import request, json, jsonify


@route_api.route("/find/beacon", methods=['GET', 'POST'])
def Beacon():
    resp = {"code": 200, "msg": "登录成功", "data": {}}
    return jsonify(resp)

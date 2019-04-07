# -*- coding: utf-8 -*-
# 小程序登录接口
from web.controllers.api import route_api
from flask import request, json, jsonify
from application import app, db
import requests, json


@route_api.route("/member/login", methods=['GET', 'POST'])
def login():
    resp = {"code": 200, "msg": "登录成功", "data": {}}
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "code不存在"
        return jsonify(resp)

    url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code".format(
        app.config['MINI_APP']['app_id'], app.config['MINI_APP']['secret_key'], code)
    r = requests.get(url)
    res = json.loads(r.text)
    openid = res['openid']

    return jsonify(resp)

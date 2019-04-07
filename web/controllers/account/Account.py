# -*- coding: utf-8 -*-

from application import app, db
from flask import Blueprint, request, redirect, jsonify
from common.libs.Helper import ops_render, iPagination, getCurrentDate
from common.models.User import User
from common.models.log.AppAccessLog import AppAccessLog
from common.libs.user.UserService import UserService
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_

route_account = Blueprint('account_page', __name__)


@route_account.route('/index')
def index():
    resp_data = {}
    req = request.values

    # 分页
    page = int(req['p']) if ('p' in req and req['p']) else 1

    if 'mix_kw' in req:
        rule = or_(User.nickname.ilike("%{0}%".format(req['nickname'])),
                   User.mobile.ilike("%{0}%".format(req['mobile'])))
        query = User.query.filter(rule)

    if 'status' in req and int(req['status']) > -1:
        query = User.query.filter(User.status == int(req['status']))

    page_params = {
        'total': User.query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    # 分页方法调用
    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page
    list = User.query.order_by(User.uid.desc()).all()[offset: limit]

    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render('account/index.html', resp_data)


@route_account.route('/info')
def info():
    resp_data = {}
    req = request.args
    uid = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/account/index")
    if uid < 1:
        return redirect(reback_url)
    info = User.query.filter_by(uid=uid).first()
    if not info:
        return redirect(reback_url)

    access_list = AppAccessLog.query.filter_by(uid=uid).order_by(AppAccessLog.id.desc()).limit(10).all()

    resp_data['info'] = info
    resp_data['access_list'] = access_list

    return ops_render('account/info.html', resp_data)


@route_account.route('/set', methods=['GET', 'POST'])
def set():
    default_pwd = "******"
    if request.method == "GET":
        resp_data = {}
        req = request.args
        uid = int(req.get("id", 0))
        user_info = None
        if uid:
            user_info = User.query.filter_by(uid=uid).first()
        resp_data['user_info'] = user_info
        return ops_render('account/set.html', resp_data)

    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的昵称！"
        return jsonify(resp)

    if mobile is None or len(mobile) < 11:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的电话号码！"
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱！"
        return jsonify(resp)

    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录用户名！"
        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录密码！"
        return jsonify(resp)

    has_in = User.query.filter(User.login_name == login_name, User.uid != id).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = "该登录名已被占用"
        return jsonify(resp)

    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        model_user = user_info
    else:
        model_user = User()
        model_user.created_time = getCurrentDate()
        model_user.login_salt = UserService.geneSalt()

    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.mobile = email
    model_user.login_name = login_name
    if login_pwd != default_pwd:
        model_user.login_pwd = UserService.genePwd(login_pwd, model_user.login_salt)

    model_user.updated_time = getCurrentDate()

    db.session.add(model_user)
    db.session.commit()

    return jsonify(resp)


@route_account.route('/ops', methods=['POST'])
def ops():
    resp = {"code": 200, "msg": "操作成功", "data": {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    action = req['action'] if 'action' in req else ''

    if not id:
        resp['code'] = -1
        resp['msg'] = "该选择要操作的账号!"
        return jsonify(resp)

    if action not in ['remove', 'recovery']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试!"
        return jsonify(resp)

    user_info = User.query.filter_by(uid=id).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "指定账号不存在!"
        return jsonify(resp)

    if action == "remove":
        user_info.status = 0
    elif action == "recovery":
        user_info.status = 1

    user_info.updated_time = getCurrentDate()

    db.session.add(user_info)
    db.session.commit()

    return jsonify(resp)

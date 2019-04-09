# -*- coding: utf-8 -*-

from flask import Blueprint, request, redirect, jsonify
from common.libs.Helper import ops_render, iPagination, getCurrentDate
from common.models.member.Member import Member
from common.libs.UrlManager import UrlManager
from application import app, db

route_member = Blueprint('member_page', __name__)


@route_member.route('/index')
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Member.query

    if 'mix_kw' in req:
        query = query.filter(Member.nickname.like("%{0}%".format(req['mix_kw'])))

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Member.status == req['status'])

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(Member.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    # 无法进行筛选TODO
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['current'] = 'index'
    return ops_render('member/index.html', resp_data)


@route_member.route('/info')
def info():
    resp_data = {}
    req = request.args
    id = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/member/index")
    if id < 1:
        return redirect(reback_url)
    info = Member.query.filter_by(id=id).first()
    if not info:
        return redirect(reback_url)

    resp_data['info'] = info
    resp_data['current'] = 'index'
    return ops_render('member/info.html', resp_data)


@route_member.route('/set', methods=['GET', 'POST'])
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.values
        id = int(req.get("id", 0))
        reback_url = UrlManager.buildUrl("/member/index")
        if id < 1:
            return redirect(reback_url)

        # 判断是否用户的id在表内存在
        # 如果不存在就直接返回index
        info = Member.query.filter_by(id=id).first()
        if not info:
            return redirect(reback_url)

        if info.status != 1:
            return redirect(reback_url)

        resp_data['info'] = info
        resp_data['current'] = 'index'
        return ops_render('member/set.html', resp_data)

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.args
    id = int(req.get("id", 0))
    nickname = str(req.get("nickname", ''))

    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名'
        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '指定的会员不存在'
        return jsonify(resp)

    member_info.nickname = nickname
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()
    return jsonify(resp)


@route_member.route('/comment')
def comment():
    return ops_render('member/comment.html', {'current': 'comment'})


@route_member.route('/ops', methods=['POST'])
def ops():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = req['id'] if 'id' in req else 0
    action = req['action'] if 'action' in req else ''
    if not id:
        resp['code'] = -1
        resp['msg'] = '请选择要操作的账号！'
        return jsonify(resp)

    if not action not in ['remove', 'recovery']:
        resp['code'] = -1
        resp['msg'] = '操作有误！'
        return jsonify(resp)

    member_info = Member.query.filter_by(id=id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '指定会员不存在'
        return jsonify(resp)

    if action == 'remove':
        member_info.status = 0
    elif action == 'recovery':
        member_info.status = 1

    member_info = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)

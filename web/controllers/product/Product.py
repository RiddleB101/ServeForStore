# -*- coding: utf-8 -*-
from decimal import Decimal

from application import app, db
from flask import Blueprint, jsonify, request, redirect
from common.libs.Helper import ops_render
from common.libs.product.ProductService import ProductService
from common.models.product.Product import Product
from common.models.product.ProductCat import ProductCat
from common.models.beacon.BeaconInfo import BeaconInfo
from common.models.product.ProductSaleChangeLog import ProductSaleChangeLog
from common.models.product.ProductStockChangeLog import ProductStockChangeLog
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrder import PayOrder
from common.models.member.Member import Member
from common.libs.Helper import getCurrentDate, iPagination, getDictFilterField
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_

route_product = Blueprint('product_page', __name__)


@route_product.route('/index')
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Product.query
    if 'mix_kw' in req:
        rule = or_(Product.name.ilike("%{0}%".format(req['mix_kw'])),
                   Product.tags.ilike(("%{0}%".format(req['mix_kw']))))
        query = query.filter(rule)

    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Product.status == req['status'])

    if 'cat_id' in req and int(req['cat_id']) > 0:
        query = query.filter(Product.cat_id == req['cat_id'])

    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(Product.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    cat_mapping = getDictFilterField(ProductCat, ProductCat.id, 'id', [])
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['cat_mapping'] = cat_mapping
    resp_data['current'] = 'index'

    return ops_render('product/index.html', resp_data)


@route_product.route('/info')
def info():
    resp_data = {}
    req = request.args
    id = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/product/index")
    if id < 1:
        return redirect(reback_url)
    info = Product.query.filter_by(id=id).first()
    if not info:
        return redirect(reback_url)
    stock_change_list = ProductStockChangeLog.query.filter(ProductStockChangeLog.product_id == id).order_by(
        ProductStockChangeLog.id.desc()).all()
    item_info = PayOrderItem.query.filter_by(product_id=id).all()
    data_item_info = []
    if item_info:
        for item in item_info:
            member_info = Member.query.filter_by(id=item.member_id).first()
            order_info = PayOrder.query.filter_by(id=item.pay_order_id).first()
            tmp_data = {
                "member_name": member_info.nickname,
                'quantity': item.quantity,
                'price': item.price,
                'status': order_info.status_desc
            }
            data_item_info.append(tmp_data)

    resp_data['info'] = info
    resp_data['stock_change_list'] = stock_change_list
    resp_data['sale_log_list'] = data_item_info
    resp_data['current'] = 'index'
    return ops_render('product/info.html', resp_data)


@route_product.route('/set', methods=['GET', 'POST'])
def set():
    if request.method == 'GET':
        resp_data = {}
        req = request.args
        id = int(req.get('id', 0))
        info = Product.query.filter_by(id=id).first()
        if info and info.status != 1:
            return redirect(UrlManager.buildUrl('/product/index'))

        cat_list = ProductCat.query.all()

        resp_data['current'] = 'index'
        resp_data['info'] = info
        resp_data['cat_list'] = cat_list
        return ops_render('product/set.html', resp_data)

    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'] else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req else 0
    beacon_id = int(req['beacon_id']) if 'beacon_id' in req else 0
    tags = req['tags'] if 'tags' in req else ''

    price = Decimal(price).quantize(Decimal('0.00'))
    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择分类"
        return jsonify(resp)

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的名称"
        return jsonify(resp)

    if price <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的价格"
        return jsonify(resp)

    if main_image is None or len(main_image) < 1:
        resp['code'] = -1
        resp['msg'] = "请上传封面图"
        return jsonify(resp)

    if summary is None or len(summary) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入描述"
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的存量"
        return jsonify(resp)

    if BeaconInfo.query.filter_by(id=beacon_id) is None:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的iBeacon ID"
        return jsonify(resp)

    if tags is None or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入标签"
        return jsonify(resp)

    product_info = Product.query.filter_by(id=id).first()
    before_stock = 0
    if product_info:
        model_product = product_info
        before_stock = model_product.stock
    else:
        model_product = Product()
        model_product.status = 1
        model_product.created_time = getCurrentDate()

    model_product.cat_id = cat_id
    model_product.name = name
    model_product.price = price
    model_product.main_image = main_image
    model_product.summary = summary
    model_product.stock = stock
    model_product.beacon_id = beacon_id
    model_product.tags = tags
    model_product.updated_time = getCurrentDate()

    db.session.add(model_product)
    ret = db.session.commit()
    ProductService.setStockChangeLog(model_product.id, int(stock) - int(before_stock), 'Back-end Modified')
    return jsonify(resp)


@route_product.route('/cat')
def cat():
    resp_data = {}
    req = request.values
    query = ProductCat.query

    # 无法筛选TODO
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(ProductCat.status == int(req['status']))

    list = query.order_by(ProductCat.weight.desc(), ProductCat.id.desc()).all()
    resp_data['list'] = list
    resp_data['search_con'] = req
    resp_data['current'] = 'cat'
    # 无法进行筛选TODO
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render('product/cat.html', resp_data)


@route_product.route('/cat-set', methods=['GET', 'POST'])
def catSet():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int(req.get("id", 0))
        info = None
        if id:
            info = ProductCat.query.filter_by(id=id).first()
        resp_data['info'] = info
        resp_data['current'] = 'index'
        return ops_render('product/cat_set.html', resp_data)

    resp = {"code": 200, "msg": "登录成功", "data": {}}
    req = request.values
    id = req['id'] if 'id' in req else ''
    name = req['name'] if 'name' in req else ''
    weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else 1
    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "code不存在"
        return jsonify(resp)

    product_cat_info = ProductCat.query.filter_by(id=id).first()
    if product_cat_info:
        model_product_cat = product_cat_info
    else:
        model_product_cat = ProductCat()
        model_product_cat.created_time = getCurrentDate()
    model_product_cat.name = name
    model_product_cat.weight = weight
    model_product_cat.updated_time = getCurrentDate()
    db.session.add(model_product_cat)
    db.session.commit()
    return jsonify(resp)


@route_product.route('/ops', methods=['POST'])
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

    product_cat_info = ProductCat.query.filter_by(id=id).first()
    if not product_cat_info:
        resp['code'] = -1
        resp['msg'] = "指定分类不存在!"
        return jsonify(resp)

    if action == "remove":
        product_cat_info.status = 0
    elif action == "recovery":
        product_cat_info.status = 1

    product_cat_info.updated_time = getCurrentDate()

    db.session.add(product_cat_info)
    db.session.commit()

    return jsonify(resp)

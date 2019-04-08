# -*- coding: utf-8 -*-
from application import app, db
from flask import Blueprint, jsonify, request
from common.libs.Helper import ops_render
from common.models.product.Product import Product
from common.models.product.ProductCat import ProductCat
from common.models.product.ProductSaleChangeLog import ProductSaleChangeLog
from common.models.product.ProductStockChangeLog import ProductStockChangeLog
from common.libs.Helper import getCurrentDate

route_product = Blueprint('product_page', __name__)


@route_product.route('/index')
def index():
    return ops_render('product/index.html')


@route_product.route('/info')
def info():
    return ops_render('product/info.html')


@route_product.route('/set')
def set():
    return ops_render('product/set.html')


@route_product.route('/cat')
def cat():
    resp_data = {}
    req = request.values
    query = ProductCat.query
    list = query.order_by(ProductCat.weight.desc(), ProductCat.id.desc()).all()
    resp_data['list'] = list
    resp_data['current'] = 'cat'
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

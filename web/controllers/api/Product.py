# -*- coding: utf-8 -*-


from web.controllers.api import route_api
from flask import request, json, jsonify, g
from application import app, db
import requests, json
from common.libs.Helper import getCurrentDate
from common.libs.UrlManager import UrlManager
from common.models.product.Product import Product
from common.models.product.ProductCat import ProductCat
from common.models.member.MemberCart import MemberCart
from sqlalchemy import or_


@route_api.route('/product/index')
def productIndex():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}

    cat_list = ProductCat.query.filter_by(status=1).order_by(ProductCat.weight.desc()).all()
    data_cat_list = []
    if cat_list:
        for item in cat_list:
            tmp_data = {
                "id": item.id,
                "name": item.name
            }
            data_cat_list.append(tmp_data)
    resp['data']['cat_list'] = data_cat_list

    product_list = Product.query.filter_by(status=1).order_by(Product.total_count.desc(), Product.id.desc()).limit(
        5).all()
    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                "id": item.id,
                "imgUrl": UrlManager.buildImageUrl(item.main_image)
            }
            data_product_list.append(tmp_data)
    resp['data']['banner_list'] = data_product_list
    return jsonify(resp)


@route_api.route('/product/search')
def productSearch():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    p = int(req['p']) if 'p' in req else 1

    if p < 1:
        p = 1

    page_size = 10
    offset = (p - 1) * page_size
    query = Product.query.filter_by(status=1)
    if cat_id > 0:
        query = query.filter_by(cat_id=cat_id)

    if mix_kw:
        rule = or_(Product.name.ilike("%{0}%".format(mix_kw)), Product.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)

    product_info = query.order_by(Product.total_count.desc(), Product.id.desc()) \
        .offset(offset).limit(page_size).all()

    data_product_info = []
    if product_info:
        for item in product_info:
            tmp_data = {
                'id': item.id,
                'name': "%s" % (item.name),
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_product_info.append(tmp_data)
    resp['data']['list'] = data_product_info
    resp['data']['has_more'] = 0 if len(data_product_info) < page_size else 1
    return jsonify(resp)


@route_api.route("/product/info")
def productInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.args
    id = int(req.get('id', 0))
    product_info = Product.query.filter_by(id=id).first()
    if not product_info or not product_info.status:
        resp['code'] = -1
        resp['msg'] = "商品已下架"
        return jsonify(resp)

    # member_info = g.member_info
    # cart_number = 0
    # if member_info:
    #     cart_number = MemberCart.query.filter_by(member_id=member_info.id).count()
    resp['data']['info'] = {
        "id": product_info.id,
        "name": product_info.name,
        "summary": product_info.summary,
        "total_count": product_info.total_count,
        # "comment_count": product_info.comment_count,
        'main_image': UrlManager.buildImageUrl(product_info.main_image),
        "price": str(product_info.price),
        "stock": product_info.stock,
        "pics": [UrlManager.buildImageUrl(product_info.main_image)]
    }
    # resp['data']['cart_number'] = cart_number
    return jsonify(resp)

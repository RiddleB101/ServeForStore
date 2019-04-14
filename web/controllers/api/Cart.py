# -*- coding: utf-8 -*-

from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.product.Product import Product
from common.models.member.MemberCart import MemberCart
from common.libs.member.CartService import CartService
from common.libs.Helper import selectFilter, getDictFiletrField
from common.libs.UrlManager import UrlManager
import json


@route_api.route("/cart/index")
def cartIndex():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '未登录'
        return jsonify(resp)

    cart_list = MemberCart.query.filter_by(member_id=member_info.id).all()
    data_cart_list = []
    if cart_list:
        product_ids = selectFilter(cart_list, 'product_id')
        product_map = getDictFiletrField(Product, Product.id, 'id', product_ids)
        for item in cart_list:
            tmp_product_info = product_map[item.product_id]
            tmp_data = {
                'id': item.id,
                'product_id': item.product_id,
                'number': item.quantity,
                'name': tmp_product_info.name,
                'price': str(tmp_product_info.price),
                'pic_url': UrlManager.buildImageUrl(tmp_product_info.main_image),
                'active': True
            }
            data_cart_list.append(tmp_data)

    resp['data']['list'] = data_cart_list
    return jsonify(resp)


@route_api.route("/cart/set", methods=["POST"])
def setCart():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    req = request.values
    product_id = int(req['id']) if 'id' in req else 0
    number = int(req['number']) if 'number' in req else 0
    if product_id < 1 or number < 1:
        resp['code'] = -1
        resp['msg'] = '添加失败-1'
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '添加失败-2'
        return jsonify(resp)

    product_info = Product.query.filter_by(id=product_id).first()
    if not product_info:
        resp['code'] = -1
        resp['msg'] = '添加失败-3'
        return jsonify(resp)

    if product_info.stock < number:
        resp['code'] = -1
        resp['msg'] = '添加失败. 库存不足!-4'
        return jsonify(resp)

    ret = CartService.setItems(member_info.id, product_id=product_id, number=number)
    if not ret:
        resp['code'] = -1
        resp['msg'] = '添加失败-5'
        print(ret)
        return jsonify(resp)

    return jsonify(resp)


@route_api.route("/cart/del", methods=["POST"])
def delCart():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)

    if not items or len(items) < 1:
        return jsonify(resp)

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '删除失败-1'
        return jsonify(resp)

    ret = CartService.deleteItems(member_id=member_info.id, items=items)
    if not ret:
        resp['code'] = -1
        resp['msg'] = '删除失败-2'
        return jsonify(resp)

    return jsonify(resp)

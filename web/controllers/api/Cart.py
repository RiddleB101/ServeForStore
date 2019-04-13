# -*- coding: utf-8 -*-

from flask import request, jsonify, g
from web.controllers.api import route_api
from common.models.product.Product import Product
from common.libs.member.CartService import CartService


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
        return jsonify(resp)

    return jsonify(resp)

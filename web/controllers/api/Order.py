# -*- coding: utf-8 -*-


from web.controllers.api import route_api
from flask import request, json, jsonify, g
from application import app, db
import requests, json, decimal
from common.libs.Helper import getCurrentDate
from common.libs.pay.PayService import PayService
from common.libs.UrlManager import UrlManager
from common.models.product.Product import Product
from common.models.product.ProductCat import ProductCat
from common.models.member.MemberCart import MemberCart
from sqlalchemy import or_
from common.libs.member.CartService import CartService


@route_api.route('/order/info', methods=['GET', 'POST'])
def orderInfo():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    product_dic = {}
    for item in params_goods_list:
        product_dic[item['id']] = item['number']

    product_ids = product_dic.keys()
    product_list = Product.query.filter(Product.id.in_(product_ids)).all()
    pay_price = decimal.Decimal(0.00)
    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image),
                'number': product_dic[item.id]
            }
            pay_price = pay_price + item.price * int(product_dic[item.id])
            data_product_list.append(tmp_data)

    resp['data']['product_list'] = data_product_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['total_price'] = str(pay_price)
    return jsonify(resp)


@route_api.route('/order/create', methods=['GET', 'POST'])
def orderCreate():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    req = request.values

    type = req['type'] if 'type' in req else ''
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)

    if len(items) < 1:
        resp['code'] = -1
        resp['msg'] = '下单失败, 请选择商品'
        return jsonify(resp)

    member_info = g.member_info
    target = PayService()
    params = {}
    resp = target.createOrder(member_info.id, items, params)

    if resp['code'] == 200 and type == 'cart':
        CartService.deleteItems(member_info.id, items)

    return jsonify(resp)

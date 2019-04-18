# -*- coding: utf-8 -*-


from web.controllers.api import route_api
from flask import request, json, jsonify, g
from application import app, db
import requests, json, decimal
from common.libs.Helper import getCurrentDate
from common.libs.pay.PayService import PayService
from common.libs.UrlManager import UrlManager
from common.models.product.Product import Product
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.product.ProductCat import ProductCat
from common.models.member.MemberCart import MemberCart
from sqlalchemy import or_
from common.libs.member.CartService import CartService


@route_api.route('/order/info', methods=['GET', 'POST'])
def orderInfo():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    req = request.values
    # order_sn = str(req.get('order_sn', ''))
    member_info = g.member_info
    # print(order_sn)
    # order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    # print(order_info)
    #
    # data_product_list = []
    # pay_price = decimal.Decimal(0.00)
    # if order_info:
    #     goods_list = PayOrderItem.query.filter_by(id=order_info.id).all()
    #     for item in goods_list:
    #         tmp_data = {
    #             'id': item.id,
    #             'name': item.name,
    #             'price': str(item.price),
    #             'pic_url': UrlManager.buildImageUrl(item.main_image),
    #             'number': item.quantity
    #         }
    #         pay_price = pay_price + item.price * int(item.quantity)
    #         data_product_list.append(tmp_data)
    #     print(data_product_list)

    params_goods = req['goods'] if 'goods' in req else None
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


@route_api.route("/order/pay", methods=["POST"])
def orderPay():
    resp = {"code": 200, "msg": "请前往收银台支付", "data": {}}
    req = request.values

    order_sn = req['order_sn'] if 'order_sn' in req else ''
    if not order_sn:
        resp['code'] = -1
        resp['msg'] = '下单失败, 请选择商品'
        return jsonify(resp)

    order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    print(order_info)
    if not order_info:
        resp['code'] = -1
        resp['msg'] = '订单出错'
        return jsonify(resp)

    return jsonify(resp)


@route_api.route("/order/ops", methods=["POST"])
def orderOps():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~"
        return jsonify(resp)

    if act == "cancel":
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=pay_order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙。请稍后再试~~"
            return jsonify(resp)
    elif act == "confirm":
        pay_order_info.express_status = 1
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()

    return jsonify(resp)

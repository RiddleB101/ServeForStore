# -*- coding: utf-8 -*-

from web.controllers.api import route_api
from flask import request, jsonify, g
from common.models.product.Product import Product
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.libs.Helper import selectFilterObj, getDictFiletrField
from common.libs.UrlManager import UrlManager
import json, datetime


@route_api.route("/my/order")
def myOrderList():
    resp = {"code": 200, "msg": "添加成功", "data": {}}
    member_info = g.member_info
    req = request.values

    status = int(req['status']) if 'status' in req else ''
    query = PayOrder.query.filter_by(member_id=member_info.id)

    if status == -8:  # 订单待付款
        query = query.filter(PayOrder.status == -8)
    elif status == 1:  # 已完成
        query = query.filter(PayOrder.status == 1)
    else:
        query = query.filter(PayOrder.status == 0)

    pay_order_list = query.order_by(PayOrder.id.desc()).all()
    data_pay_order_list = []
    if pay_order_list:
        pay_order_ids = selectFilterObj(pay_order_list, "id")
        pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids))
        product_ids = selectFilterObj(pay_order_item_list, 'product_id')
        product_map = getDictFiletrField(Product, Product.id, 'id', product_ids)
        pay_order_item_map = {}
        if pay_order_item_list:
            for item in pay_order_item_list:
                if item.pay_order_id not in pay_order_item_map:
                    pay_order_item_map[item.pay_order_id] = []

                tmp_product_info = product_map[item.product_id]
                pay_order_item_map[item.pay_order_id].append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'pic_url': UrlManager.buildImageUrl(tmp_product_info.main_image),
                    'name': tmp_product_info.name
                })

        for item in pay_order_list:
            tmp_data = {
                "status": item.status,
                "date": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "order_number": item.order_number,
                "order_sn": item.order_sn,
                "note": item.note,
                "total_price": str(item.total_price),
                "goods_list": pay_order_item_map[item.id]
            }
            data_pay_order_list.append(tmp_data)

    resp['data']['pay_order_list'] = data_pay_order_list
    return jsonify(resp)

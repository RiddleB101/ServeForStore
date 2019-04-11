# -*- coding: utf-8 -*-


from web.controllers.api import route_api
from flask import request, json, jsonify
from application import app, db
import requests, json
from common.libs.Helper import getCurrentDate
from common.libs.UrlManager import UrlManager
from common.models.product.Product import Product
from common.models.product.ProductCat import ProductCat


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

    product_list = Product.query.filter_by(status=1).order_by(Product.total_count.desc(), Product.id.desc()).limit(5).all()
    data_product_list = []
    if product_list:
        for item in product_list:
            tmp_data = {
                "id": item.id,
                "imgUrl": UrlManager.buildUrl(item.main_image)
            }
            data_product_list.append(tmp_data)
    resp['data']['banner_list'] = data_product_list
    return jsonify(resp)


def productSearch():
    return

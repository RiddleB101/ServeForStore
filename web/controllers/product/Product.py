# -*- coding: utf-8 -*-

from flask import Blueprint, render_template
from common.libs.Helper import ops_render

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
    return ops_render('product/cat.html')


@route_product.route('/cat-set')
def catSet():
    return ops_render('product/cat_set.html')

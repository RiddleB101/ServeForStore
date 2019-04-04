# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

route_product = Blueprint('product_page', __name__)


@route_product.route('/index')
def index():
    return render_template('product/index.html')


@route_product.route('/info')
def info():
    return render_template('product/info.html')


@route_product.route('/set')
def set():
    return render_template('product/set.html')


@route_product.route('/cat')
def cat():
    return render_template('product/cat.html')


@route_product.route('/cat-set')
def catSet():
    return render_template('product/cat_set.html')

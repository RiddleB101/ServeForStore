# -*- coding: utf-8 -*-
# HTTP模块相关初始化
from application import app
from web.controllers.index import route_index

app.register_blueprint(route_index, url_prefix="/")

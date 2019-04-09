# -*- coding: utf-8 -*-
# HTTP模块相关初始化


from web.interceptors.AuthInterceptor import *
from web.interceptors.ErrorInterceptor import *

from application import app

from web.controllers.index import route_index
from web.controllers.user.User import route_user
from web.controllers.account.Account import route_account
from web.controllers.member.Member import route_member
from web.controllers.finance.Finance import route_finance
from web.controllers.product.Product import route_product
from web.controllers.stat.Stat import route_stat
from web.controllers.static import route_static
from web.controllers.api import route_api
from web.controllers.upload.Upload import route_upload

app.register_blueprint(route_index, url_prefix="/")
app.register_blueprint(route_user, url_prefix="/user")
app.register_blueprint(route_account, url_prefix="/account")
app.register_blueprint(route_member, url_prefix="/member")
app.register_blueprint(route_finance, url_prefix="/finance")
app.register_blueprint(route_product, url_prefix="/product")
app.register_blueprint(route_stat, url_prefix="/stat")
app.register_blueprint(route_static, url_prefix="/static")
app.register_blueprint(route_api, url_prefix="/api")
app.register_blueprint(route_upload, url_prefix="/upload")
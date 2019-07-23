# -*- coding: utf-8 -*-
# 本地开发环境配置
SERVER_PORT = 5000
DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'mysql://root:@127.0.0.1/product_db?charset=utf8mb4'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf8mb4"

AUTH_COOKIE_NAME = "product_store"
# 过滤URL
IGNORE_URLS = [
    "^/user/login"
]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]

# 前端api过滤URL
API_IGNORE_URLS = [
    "^/api/member/login",
    "^/api/product"
]

PAGE_SIZE = 50
PAGE_DISPLAY = 10

STATUS_MAPPING = {
    "1": "NORMAL",
    "0": "DELETED"
}

MINI_APP = {
    "app_id": "",
    "app_key": "",
    "pay_key": "",
    "mch_id": "",
    "callback_url": "/api/order/callback"
}

UPLOAD = {
    'ext': ['jpg', 'gif', 'png', 'jpeg'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    'domain': "http://127.0.0.1:5000"
}

PAY_STATUS_MAPPING = {
    "1": "COMPLETED",
    "-8": "TO BE PAID",
    "0": "CLOSED"
}

PAY_STATUS_DISPLAY_MAPPING = {
    "0": "CLOSED",
    "1": "PAID",
    "-8": "TO BE PAID",
    "-6": "TO BE CONFIRMED",
    "-5": "TO BE COMMENTED"
}

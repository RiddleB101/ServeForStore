# -*- coding: utf-8 -*-
# user的服务类，用于编写加密密码和解密密码的方法，其他服务类也可以放在这里
import base64
import hashlib
import random
import string


class UserService():
    # 加密cookie, 登录态认证码
    @staticmethod
    def geneAuthCode(user_info=None):
        m = hashlib.md5()
        str = "%s-%s-%s-%s" % (user_info.uid, user_info.login_name, user_info.login_pwd, user_info.login_salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    # 加密密码
    @staticmethod
    def genePwd(pwd, salt):
        m = hashlib.md5()
        str = "%s-%s" % (base64.encodebytes(pwd.encode("utf-8")), salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        return ("".join(keylist))

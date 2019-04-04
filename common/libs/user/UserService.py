# -*- coding: utf-8 -*-
# user的服务类，用于编写加密密码和解密密码的方法，其他服务类也可以放在这里
import base64
import hashlib


class UserService():
    @staticmethod
    def genePwd(pwd, salt):
        m = hashlib.md5()
        str = "%s-%s" % (base64.encodebytes(pwd.encode("utf-8")), salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

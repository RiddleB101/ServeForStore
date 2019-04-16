# -*- coding: utf-8 -*-
# user的服务类，用于编写加密密码和解密密码的方法，其他服务类也可以放在这里
import base64
import hashlib, random, string, requests, json
from application import app


class MemberService():
    # 加密cookie, 登录态认证码
    @staticmethod
    def geneAuthCode(member_info=None):
        m = hashlib.md5()
        str = "%s-%s-%s" % (member_info.id, member_info.salt, member_info.status)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        return ("".join(keylist))

    @staticmethod
    def getWeChatOpenId(code):
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code".format(
            app.config['MINI_APP']['app_id'], app.config['MINI_APP']['app_key'], code)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = None
        if 'openid' in res:
            openid = res['openid']
        return openid

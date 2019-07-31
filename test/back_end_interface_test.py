# -*- coding: utf-8 -*-

import requests
import unittest


class TokenClass(unittest.TestCase):
    def setUp(self):
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }
        self.url = 'https://enigmazzz.cn'

    def getToken(self):
        data = {
            'password': '816440c40b7a9d55ff9eb7b20760862c',
            'login_name': 'root'
        }
        self.r = requests.post(self.url + '/user/login', json=data, headers=self.headers)
        return {'cookies': self.r.cookies.get_dict()}

    def test_getAccountInfo(self):
        self.getToken()
        self.r = requests.get(self.url + '/account/index', headers=self.headers)
        print(self.r.text)
        return {"text": self.r.text, "code": self.r.status_code}

    def tearDown(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TokenClass)
    unittest.TextTestRunner(verbosity=2).run(suite)

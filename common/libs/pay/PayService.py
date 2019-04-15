# -*- coding: utf-8 -*-
import decimal, time, hashlib, random
from application import app, db
from common.models.product.Product import Product
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrderCallbackData import PayOrderCallbackDatum
from common.libs.Helper import getCurrentDate
from common.libs.product.ProductService import ProductService


class PayService():
    def __init__(self):
        pass

    def createOrder(self, member_id, items=None, params=None):
        resp = {"code": 200, "msg": "添加成功", "data": {}}
        pay_price = decimal.Decimal(0.00)
        continue_count = 0
        product_id = []
        for item in items:
            if decimal.Decimal(item['price']) < 0:
                continue_count += 1
                continue
            pay_price = pay_price + decimal.Decimal(item['price']) * int(item['number'])
            product_id.append(item['id'])

        if continue_count >= len(items):
            resp['code'] = -1
            resp['msg'] = '商品为空'
            return resp

        note = params['note'] if 'params' and 'note' in params else ''

        total_price = pay_price

        # 并发控制, 悲观锁
        try:
            tmp_product_list = db.session.query(Product).filter(Product.id.in_(product_id)).with_for_update().all()

            tmp_product_stock_mapping = {}
            for tmp_item in tmp_product_list:
                tmp_product_stock_mapping[tmp_item.id] = tmp_item.stock

            model_pay_order = PayOrder()
            # 提交给支付平台的凭证码, 不能重复
            model_pay_order.order_sn = self.geneOrderSn()
            model_pay_order.member_id = member_id
            model_pay_order.total_price = total_price
            model_pay_order.pay_price = pay_price
            model_pay_order.note = note
            model_pay_order.status = -8
            model_pay_order.updated_time = model_pay_order.created_time = getCurrentDate()
            db.session.add(model_pay_order)

            for item in items:
                tmp_left_stock = tmp_product_stock_mapping[item['id']]
                print(tmp_left_stock)
                print(item['number'])
                if decimal.Decimal(item['price']) < 0:
                    continue
                if int(item['number']) > int(tmp_left_stock):
                    raise Exception("库存不足")

                tmp_ret = Product.query.filter_by(id=item['id']).update({
                    'stock': int(tmp_left_stock) - int(item['number'])
                })

                if not tmp_ret:
                    raise Exception("下单失败")

                tmp_pay_item = PayOrderItem()
                tmp_pay_item.pay_order_id = model_pay_order.id
                tmp_pay_item.member_id = member_id
                tmp_pay_item.quantity = item['number']
                tmp_pay_item.price = item['price']
                tmp_pay_item.product_id = item['id']
                tmp_pay_item.note = note
                tmp_pay_item.updated_time = tmp_pay_item.created_time = getCurrentDate()
                db.session.add(tmp_pay_item)
                ProductService.setStockChangeLog(item['id'], -item['number'], 'Online Sale')

            db.session.commit()
            resp['data'] = {
                'id': model_pay_order.id,
                'order_sn': model_pay_order.order_sn,
                'total_price': str(total_price)
            }
        except Exception as e:
            db.session.rollback()
            print(e)
            resp['code'] = -1
            resp['msg'] = '下单失败'
            resp['err_msg'] = str(e)

        return resp

    def geneOrderSn(self):
        m = hashlib.md5()
        sn = None
        while True:
            str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 99999999))
            m.update(str.encode("utf-8"))
            sn = m.hexdigest()
            if not PayOrder.query.filter_by(order_sn=sn).first():
                break

        return sn

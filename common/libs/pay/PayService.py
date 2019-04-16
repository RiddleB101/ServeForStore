# -*- coding: utf-8 -*-
import decimal, time, hashlib, random
from application import app, db
from common.models.product.Product import Product
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.product.ProductStockChangeLog import ProductStockChangeLog
from common.models.product.ProductSaleChangeLog import ProductSaleChangeLog
from common.models.pay.PayOrderCallbackData import PayOrderCallbackDatum
from common.libs.Helper import getCurrentDate
from common.libs.product.ProductService import ProductService
from common.libs.queue.QueueService import QueueService


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

    def closeOrder(self, pay_order_id=0):
        if pay_order_id < 1:
            return False
        pay_order_info = PayOrder.query.filter_by(id=pay_order_id, status=-8).first()
        if not pay_order_info:
            return False

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
        if pay_order_items:
            # 需要归还库存
            for item in pay_order_items:
                tmp_product_info = Product.query.filter_by(id=item.product_id).first()
                if tmp_product_info:
                    tmp_product_info.stock = tmp_product_info.stock + item.quantity
                    tmp_product_info.updated_time = getCurrentDate()
                    db.session.add(tmp_product_info)
                    db.session.commit()
                    ProductService.setStockChangeLog(item.product_id, item.quantity, "订单取消")

        pay_order_info.status = 0
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return True

    def orderSuccess(self, pay_order_id=0, params=None):
        try:
            pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
            if not pay_order_info or pay_order_info.status not in [-8, -7]:
                return True

            pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''
            pay_order_info.status = 1
            pay_order_info.express_status = -7
            pay_order_info.updated_time = getCurrentDate()
            db.session.add(pay_order_info)

            pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
            for order_item in pay_order_items:
                tmp_model_sale_log = ProductSaleChangeLog()
                tmp_model_sale_log.product_id = order_item.product_id
                tmp_model_sale_log.quantity = order_item.quantity
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
                tmp_model_sale_log.created_time = getCurrentDate()
                db.session.add(tmp_model_sale_log)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return False

        # 加入通知队列，做消息提醒和
        QueueService.addQueue("pay", {
            "member_id": pay_order_info.member_id,
            "pay_order_id": pay_order_info.id
        })
        return True

    def addPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        model_callback = PayOrderCallbackDatum()
        model_callback.pay_order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

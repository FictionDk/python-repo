# -*- coding: utf-8 -*-

import pika
import utils
import sys
import json

class MockDataBuilder:
    def __init__(self, order_type):
        '''初始化模拟数据生成对象
        Args order_type 模拟数据的类型,包括:
            DEVICE_REGISTE : 设备注册
            DEVICE_HEARTBEAT : 设备心跳
            TAG_QUERY : 血袋标签查询
            BLOOD_CHECK : 血袋安全检测
            BLOOD_BAND : 血袋与储血筐绑定
            BLOOD_IN : 储血筐入库
            BLOOD_PREPARE : 备血
            BLOOD_OUT : 订单出库
        '''
        self.__order_type = order_type
        self.__device_no = 'vkOV6ZnwjIw7Y2qV'

    def mock_req_data(self):
        '''创建模拟的请求
            deviceNo;
            orderType;
            requestBody;
        '''
        order_req = {}
        order_req['deviceNo'] = self.__device_no
        order_req['orderType'] = self.__order_type
        if self.__order_type == 'DEVICE_REGISTE':
            order_req['requestBody'] = self.__build_regist_data()
        else:
            order_req = None
        return order_req

    def __build_regist_data(self):
        '''创建模拟的设备注册数据
        '''
        device = {}
        device['name'] = '科冷贴标机'
        return json.dumps(device)

conf = utils.get_config()

credentials = pika.PlainCredentials(conf["username"],conf["password"])
conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
)

channel = conn.channel()
channel.queue_declare(queue='iot.bus.queue',durable=True)

iot_order_type = sys.argv[1] if len(sys.argv) > 1 else 'DEVICE_HEARTBEAT'
builder = MockDataBuilder(iot_order_type)
req_data = builder.mock_req_data()

if req_data is not None:
    msg = json.dumps(req_data)
    channel.basic_publish(exchange='', routing_key='iot.bus.queue', body=msg,
        properties=pika.BasicProperties(content_type='application/json'))
    print(" [x] Sent %r" % str(msg))

conn.close()

# -*- coding: utf-8 -*-

import pika
import utils
import os
import sys
WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
ES_DIR = os.path.join(WORK_DIR,"es")
sys.path.append(ES_DIR)
from core import ESConnect

es_until = ESConnect()
exchange_name = 'ex.healthcare.fanout.logs'

conf = utils.get_config()

credentials = pika.PlainCredentials(conf["username"],conf["password"])

conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
    )

channel = conn.channel()

channel.exchange_declare(exchange=exchange_name,exchange_type='fanout')
result = channel.queue_declare(queue='', durable=True, exclusive=True)

queue_name = result.method.queue

channel.queue_bind(exchange=exchange_name,queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    print(type(body))
    body = str(body, encoding='utf-8')
    es_until.recive_log(body)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

# -*- coding: utf-8 -*-

import pika
import utils

conf = utils.get_config()

credentials = pika.PlainCredentials(conf["username"],conf["password"])
conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
)

channel = conn.channel()

channel.exchange_declare(exchange='iot.order.fanout',exchange_type='fanout')
result = channel.queue_declare(queue='', durable=False, exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='iot.order.fanout',queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch,method,properties,body):
    print("[x] %r:%r" % (method.routing_key,body))

channel.basic_consume(queue_name,callback,auto_ack=True)

channel.start_consuming()

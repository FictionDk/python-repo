# -*- coding: utf-8 -*-

import pika
import time
import utils

conf = utils.get_config()

credentials = pika.PlainCredentials(conf["username"],conf["password"])

conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
    )

channel = conn.channel()

channel.exchange_declare(exchange='logs',exchange_type='fanout')
result = channel.queue_declare(queue='', durable=True, exclusive=True)

queue_name = result.method.queue

channel.queue_bind(exchange='logs',queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
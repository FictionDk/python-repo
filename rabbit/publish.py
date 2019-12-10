# -*- coding: utf-8 -*-

import pika
import sys
import utils

conf = utils.get_config()

credentials = pika.PlainCredentials(conf["username"],conf["password"])

conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
    )

channel = conn.channel()
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"

channel.basic_publish(exchange='logs', routing_key='', body=message)

print(" [x] Sent %r" % message)

conn.close()
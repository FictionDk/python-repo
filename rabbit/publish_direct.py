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

channel.exchange_declare(exchange='direct_logs',exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(
    exchange='direct_logs', routing_key=severity, body=message)
print(" [x] Sent %r:%r" % (severity, message))

conn.close()
# -*- coding: utf-8 -*-

import pika
import time
import utils
import sys

conf = utils.get_config()

credentials = pika.PlainCredentials(conf["username"],conf["password"])
conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
    )

channel = conn.channel()

channel.exchange_declare(exchange='topic_logs',exchange_type='topic')
result = channel.queue_declare(queue='', durable=True, exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(queue_name,'topic_logs',routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch,method,properties,body):
    print("[x] %r:%r" %(method.routing_key,body))

channel.basic_consume(queue_name,callback,auto_ack=True)

channel.start_consuming()
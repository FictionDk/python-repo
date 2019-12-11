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

channel.exchange_declare(exchange='direct_logs',exchange_type='direct')
result = channel.queue_declare(queue='', durable=True, exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
    sys.stderr.write("Useing: %s [info] [waring] [error] \n" % sys.argv[0])
    sys.exit(1)

for severity in severities:
    channel.queue_bind(exchange='direct_logs',queue=queue_name,routing_key=severity)

print('[*] Waiting for logs. To exit press CTRL+C')

def callback(ch,method,properities,body):
    print("[x] %r:%r" % (method.routing_key,body))

channel.basic_consume(queue=queue_name,on_message_callback=callback,auto_ack=True)

channel.start_consuming()

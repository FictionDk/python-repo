# -*- coding: utf-8 -*-

import pika
import time
#import utils
#conf = utils.get_config()

conf = {'url':'172.16.xxx.xxx','username':'lims','port':5672,'password':'xxx','vhost':'xxx'}

credentials = pika.PlainCredentials(conf["username"],conf["password"])

conn = pika.BlockingConnection(
    pika.ConnectionParameters(host=conf["url"],port=conf["port"],virtual_host=conf["vhost"],
        credentials=credentials)
    )

channel = conn.channel()

channel.exchange_declare(exchange='lims.direct',exchange_type='direct')
result = channel.queue_declare(queue='lims.sample', durable=True, exclusive=True)

#queue_name = result.method.queue

channel.queue_bind(exchange='amq.direct',queue="lims.sample")

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    #utils.save_log(body)

channel.basic_consume(
    queue="lims.sample", on_message_callback=callback, auto_ack=True)

channel.start_consuming()
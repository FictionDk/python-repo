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

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch,method,properties,body):
    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count = 1)
channel.basic_consume(queue="task_queue", on_message_callback=callback)

channel.start_consuming()

# coding: UTF-8
import os
import sys
import pika
def createVerifyCardQueues():
    credentials = pika.PlainCredentials('mangkhut', 'cQ7RbSDQ')
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.110.94',82,"mkt",credentials))
    channel = connection.channel()
 
    name_prefix = "merchant.verifycard.async"
    exchange_name = "mkt.direct"
    channel.queue_declare()
    start=10
    end = 26
    for biz_type in range(start, end):
        queue_name = name_prefix + str(biz_type)
        channel.queue_declare(queue_name,False,True)
        channel.queue_bind(queue_name,exchange_name,queue_name)
 
if __name__ == "__main__":
    createVerifyCardQueues()
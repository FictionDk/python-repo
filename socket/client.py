# -*- coding: utf-8 -*-
import socket

try:
    client = socket.socket()
    client.connect(('127.0.0.1',8089))
    client.send(bytes('QUERY TIME ORDER\n',encoding='utf-8'))
    print("Waiting...")
    data = client.recv(1024)
    print("Geting..." + str(data))
    if data:
        print(data.decode())
except ConnectionResetError:
    print('连接中断！')
except ConnectionRefusedError:
    print('连接被拒绝')
else:
    client.close()

# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 16:43:25 2018

连接客户端类

@author: dk
"""

from websocket import create_connection

class MudClient():
    def __init__(self,auth,url):
        self.auth = auth
        self.url = url
    
    def login(self):
        self.conn = create_connection(self.url)
        self.conn.send(self.auth['user']+" "+self.auth['pwd'])
        self.conn.send("login "+self.auth['uid'])
        self.conn.send("score")
        self.name = self.auth['rName']
        self.id = self.auth['uid']

    def doCommond(self,commond):
        self.conn.send(commond)

    def flush(self):
        return self.conn.recv()

    def close(self):
        self.conn.close()
        print("%s 断开连接"%self.auth['rName'])
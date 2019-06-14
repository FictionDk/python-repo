# -*- coding: utf-8 -*-
from mysqlClient import MySqlClient
class FlyDB ():
    def __init__(self,dbType):
        self.__dbType = dbType
        if dbType == "mysql":
            host = '192.168.110.94'
            port = 3306
            user = 'root'
            pwd = 'stpass'
            db = 'berry_sup'
            self.__dbClient = MySqlClient(host,port,user,pwd,db)
        else:
            print("db no support")

    def insert_value(self,date):
        if self.__dbType == "mysql":
            sql = 'update body_check set check_date = %s where id = %s;'
            self.__dbClient.dosqlBatch(sql,date)

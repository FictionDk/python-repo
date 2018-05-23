#coding=utf-8
import pymysql
class MySqlClient():
	def __init__(self,host,port,user,pwd,db):
		self.conn = None
		self.host = host
		self.port = port
		self.user = user
		self.pwd = pwd
		self.db = db

	def __getConn(self):
		if self.conn is None:
			return pymysql.connect(host=self.host,port=self.port,user=self.user,
				password=self.pwd,db=self.db,charset="UTF8")
		else:
			return self.conn

	def dosql(self,sql):
		conn = self.__getConn()
		cursor = conn.cursor()

	def dosqlBatch(self,sql,dates):
		conn = self.__getConn()
		cursor = conn.cursor()
		cursor.executemany(sql,dates)
		conn.commit()
#coding=utf-8
from mysqlClient import MySqlClient
class FlyDB ():
	def __init__(self,dbType):
		self.__dbType = dbType
		if dbType == "mysql":
			host='192.168.110.94'
			port=3306
			user='root'
			pwd='stpass'
			db='spider_db'
			self.__dbClient = MySqlClient(host,port,user,pwd,db)
		else:
			print("db no support")

	def insertValue(self,date):
		if self.__dbType == "mysql":
			sql = 'replace into fly_price(airline,save_date,fromdis,todis,departingtime,price,content)values(%s,%s,%s,%s,%s,%s,%s)'
			self.__dbClient.dosqlBatch(sql,date)
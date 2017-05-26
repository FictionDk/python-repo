# encoding: utf-8
"""
根据用户购买数据将用户聚类
根据聚类结果向用户推荐商品
"""
import numpy as np
import pymysql
import time

_DEBUG = False

def getConnect(confFileName):
    fr = open(confFileName,encoding="utf-8")
    confArray = fr.readlines()
    conf = {}
    for line in confArray:
        line = line.strip()
        line = line.split(":")
        conf[line[0]] = line[1]

    conn = pymysql.connect(host=conf['host'],port=int(conf['port']),user=conf['user'],
                password=conf['password'],db=conf['db'],charset="UTF8")
    return conn
    
def getOrderList(conn):
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select id,order_no,user_id from jjg_order where id > 467 and status = 5 and for_seller = 0"
    effectRowNum = cursor.execute(sql)
    return cursor

def getOrderGoods(cursor,orderId):
    sql = "select goods_id,goods_nums,real_price from jjg_order_goods where order_id = "+str(orderId)
    effectRowNum = cursor.execute(sql)    
    return cursor.fetchall() 

def cleanData(conn,rows):
    cursor = conn.cursor()
    index = 0
    num = 800
    
    for item in rows:
        orderGoods = getOrderGoods(cursor,item['id'])
        for good in orderGoods:
            insertToUserGoods(cursor,item['user_id'],good[0],good[1])  
            index += 1
            if index % num == 0:
                conn.commit()

def insertToUserGoods(cursor,userId,goodId,goodNum):
    sql = "select id,goods_nums from jjg_user_commend_goods where user_id = "+str(userId)+" and goods_id = "+str(goodId)       
    effectNum = cursor.execute(sql)
    if effectNum > 0:
        row = cursor.fetchone()
        goodNum = row[1] + goodNum
        sql = "update jjg_user_commend_goods set goods_nums = "+str(goodNum)+" where id = "+str(row[0])
        cursor.execute(sql)
    else:
        sql = "insert into jjg_user_commend_goods(user_id,goods_id,goods_nums)values(%s,%s,%s)"
        cursor.executemany(sql,[(userId,goodId,goodNum)])

def main():
    if _DEBUG == True:
        import pdb
        pdb.set_trace()
    fileName = "conf.property"
    startTime = time.time()
    print(startTime)
    conn = getConnect(fileName)
    cursor = getOrderList(conn)
    rows = cursor.fetchall()
    cleanData(conn,rows)
    endTime = time.time()
    print(endTime)
    print(endTime-startTime)

    cursor.close()
    conn.close()




# encoding: utf-8
"""
根据用户购买数据将用户聚类
根据聚类结果向用户推荐商品
"""
import numpy as np
import matplotlib.pyplot as plt
import pymysql
import time
#from sklearn.cluster import KMeans
_DEBUG = False

#根据文件名选择合适的数据库连接
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
    
#获取订单列表
def getOrderList(conn):
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = "select id,order_no,user_id from jjg_order where id > 467 and status = 5 and for_seller = 0"
    effectRowNum = cursor.execute(sql)
    return cursor

#获取订单所属商品
def getOrderGoods(cursor,orderId):
    sql = "select goods_id,goods_nums,real_price from jjg_order_goods where order_id = "+str(orderId)
    effectRowNum = cursor.execute(sql)    
    return cursor.fetchall() 


def updataCommendGoods(conn,rows):
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
    cursor.close()

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

def createDataArray(conn):
    sql = "select distinct user_id from jjg_user_commend_goods"
    cursor = conn.cursor()
    cursor.execute(sql)
    userArray = cursor.fetchall()
    rowNum = len(userArray)
    retData = np.zeros((rowNum,10),dtype=np.int)
    vector = np.zeros((rowNum,1),dtype=np.int)
    index = 0
    for user in userArray:
        userId = user[0]
        sql = "select cg.*,e.category_id from jjg_user_commend_goods as cg left join jjg_category_extend as e on e.goods_id =\
            cg.goods_id where user_id ="+str(userId)+" order by goods_nums desc"
                            
        cursor.execute(sql)
        rows = cursor.fetchall()
        goodList = []
        cateList = []
        goodList.clear()
        for i in range(10):
            if i < len(rows):
                goodList.append(rows[i][2])
                cateList.append(rows[i][6] if rows[i][6] != None else 0)
            else:
                goodList.append(0)
                cateList.append(0)
        print(len(cateList))
        print(cateList[:5])

        vector[index,:] = user
        retData[index,:] = cateList
        index += 1
    
    cursor.close()
            
    return vector,retData

#分类用户
def createRetDataAndLabel():
    fileName = "conf.property"
    conn=getConnect(fileName)
    userLabel,retData = createDataArray(conn)
    np.save("retData.npy",retData)
    np.save("userLabel.npy",userLabel)
    return userLabel,retData

#获取分类后的用户
def getUserLabel(vector,retData):
    km = KMeans(n_clusters = 20)
    result = km.fit_predict(retData)
    userList = vector[:,0].tolist()
    
    userLabel = {}
    for i in range(len(userList)):
        userLabel[str(result[i])] = str(userLabel[str(result[i])])+","+str(userList[i])
    return userLabel

#分割数据
#返回的数据
def cutData(result,user,reduceData):
    fig,ax = plt.subplots()
        
    userList = user[:,0],tolist()
    userLabel = {}
    for i in range(len(userList)):
        userLabel[str(result[i])] = str(userLabel[str(result[i])])+","+str(userList[i])
    
    
def main():
    if _DEBUG == True:
        import pdb
        pdb.set_trace()
    fileName = "conf.property"
    startTime = time.time()
    print(startTime)
    
    conn = getConnect(fileName)
    #获取所有已经完成订单数据
    cursor = getOrderList(conn)
    rows = cursor.fetchall()
    #更新userCommendGoods表
    updataCommendGoods(conn,rows)
    #准备聚类数据
    ndArray = createDataArray(conn)
    
    endTime = time.time()
    print(endTime)
    print(endTime-startTime)

    cursor.close()
    conn.close()




# encoding: utf-8
"""
获取操作mysql游标,操作数据库:
"""
import pymysql
_DEBUG = False

def getConnect():
    confFileName = getConfig()
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

def getConfig():
    if _DEBUG == True:
        import pdb
        pdb.set_trace()

    print("chose config property,ali or test?")
    fileName = "conf_ali.property"
    fileInput = input()
    if fileInput == 'ali':
        fileName = "conf_ali.property"
    elif fileInput == 'test':
        fileName = "conf_test.property"
    else:
        print("chose default config property conf_ali.property")
    return fileName
    
def getDicCursor(conn):
    return conn.cursor(cursor=pymysql.cursors.DictCursor)

def getCursor(conn):
    return conn.cursor()

def doSelect(sql,cursor):
    num = cursor.execute(sql)
    return cursor.fetchall()

def printList(arr):
    for item in arr:
        print(item)

def query(conn):
    cursor = conn.cursor()
    print("请输入查询语句,输入q跳出查询!")
    sql = ''
    while sql != 'q':
        sql = input()
        try:
            arr = doSelect(sql,cursor)
            printList(arr)
        except Exception as err:
            print('Error:',err)
            
    cursor.close()

# 删除jjg_test里多余数据脚本    
def deleteScrip(conn):
    cursor = conn.cursor()
    sql = "select id,name,seller_id from jjg_goods where seller_id = 98"
    goodList = doSelect(sql,cursor)
    index = 0
    num = 800
    for good in goodList:
        goodId = str(good[0])
        delSqlR = "delete from jjg_goods_photo_relation where goods_id = "+str(goodId)
        delSqlC = "delete from jjg_category_extend where goods_id = "+str(goodId)        
        cursor.execute(delSqlR)
        cursor.execute(delSqlC)
        index += 1
        print(good)
        print(str(index)+"删除成功")
        
        if index%num == 0:
            conn.commit()
    conn.commit()
    cursor.close()
    
    
        
    




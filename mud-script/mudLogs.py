# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 17:11:38 2018

日志记录

@author: dk
"""
import time
import demjson

global __outfile
__fileName = "./log/mud.log"
__msgFileName = "./log/mud_msg.log"
__noTypeFile = "./log/mud_none_type.log"
__fileos = open(__fileName,'a')
__msgfileos = open(__msgFileName,'a')
__notypefileos = open(__noTypeFile,'a')

def decode(value):
    try:
        valueDict = demjson.decode(value,encoding="utf-8")
        return valueDict,True
    except:
        return value,False
    
def info(msg):
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    result,flag = decode(msg)
    msg = timeStr + " -- " +str(result)+" \n"
    print(msg)
    if flag:
        if result.get("type") == "msg":
            try:
                __msgfileos.write(msg)
                __msgfileos.flush()
            except UnicodeError:
                __msgfileos.write("[emoj表情]")
        else:
            __fileos.write(msg)
            __fileos.flush()
    else:
        __notypefileos.write(msg)
        __notypefileos.flush()
    return result,flag
    
def close():
    __fileos.close()
    __msgfileos.close()
    __notypefileos.close()
    print("=====文件流关闭====")      

def test():
    info("test11111111111")
    info("test22222222222")
    info("test33333333333")
    close()

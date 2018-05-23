# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 10:52:13 2018

@author: dk
"""

import mudUtils as utils
import mudLogs as logger
from mudClient import MudClient
from mineTaskMatchine import MineTaskMatchine
from mudTask import TaskMachine,TaskStatus
import time

class GoodUseMatchine():
    def __init__(self,goodName,npcId):
        self.goodName = goodName
        self.goodId = None
        self.__goodCount = 0
        self.__isStart = False
        self.__notHasGood = False
        self.__npcId = npcId
        self.isOpen = False
        
    def open(self):
        self.isOpen = True
        if self.__isStart is False:
            self.__isStart = True
            return ["stopstate","pack"]
 
    def close(self):
        self.__isStart = False
        self.goodName = None
        self.goodId = None
        self.__goodCount = 0
        self.__isStart = False
        self.__notHasGood = False
        self.__npcId = None
        self.isOpen = False
        print("==matchine close==")

    def __loadPack(self,msg):
        if msg.get('items') is not None:
            for good in msg.get('items'):
                if self.goodName in good.get("name"):
                    print("===%s been get==="%self.goodName)
                    self.goodId = good.get("id")
                    self.__goodCount = good.get("count")
                    break
            self.__notHasGood = True

    def __useGood(self):
        if self.goodId is not None:
            flows = []
            for i in range(self.__goodCount):
                if i > 5:
                    break
                flows.append("use "+self.goodId)
            return flows
        
    def __load(self,msg):
        if type(msg) is dict and msg.get("dialog") == "pack" :
            self.__loadPack(msg)
        
    def mathineDo(self,msg):
        self.__load(msg)
        if self.goodId is not None:
            print("===id [%s] been get==="%self.goodId)
            flows = self.__useGood()
            self.close()
            return flows

def doCommond(mudRole,flows):
    if flows is None:
        return None
    for commond in flows:
        if commond is None:
            return None
        logger.info(mudRole.name+": do ["+commond+"]")
        mudRole.doCommond(commond)
        time.sleep(0.5)

def test():
    name = "闻人晓"
    auth,socket_url = utils.getRoleConfig(name)
    mud = MudClient(auth,socket_url)
    mud.login()
    mineTask = MineTaskMatchine(name,TaskStatus.STARTING)
    goodUseMatchine = GoodUseMatchine("养精丹",None)
    flows = goodUseMatchine.open()
    doCommond(mud,flows)
    for i in range (100):
        value = mud.flush()
        msg,flag = logger.info(value)
        if goodUseMatchine.isOpen is True:
            flows = goodUseMatchine.mathineDo(msg)
        else:
            flows = mineTask.doTask(msg)
        doCommond(mud,flows)
    mud.close()
    logger.close()

#test()

    
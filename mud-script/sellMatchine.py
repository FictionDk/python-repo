# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 18:36:42 2018

@author: dk
"""
import mudUtils as utils

class SellMatchine():
    def __init__(self,name):
        self.__name = name
        self.__npcName = "杨永福"
        self.__npcId = None
        self.__goods = []
        # goods which prepared to be sell
        self.__sellPack = []
        self.isOpen = False
        self.__isStart = False

    def toDict(self):
        objDict = {}
        objDict['__name'] = self.__name
        objDict['__npcName'] = self.__npcName
        objDict['__npcId'] = self.__npcId
        objDict['__goods'] = self.__goods
        objDict['__sellPack'] = self.__sellPack
        objDict['isOpen'] = self.isOpen
        objDict['__isStart'] = self.__isStart
        return objDict
        
    def __goodIsForSell(self,goodName):
        if goodName is None:
            return False
        if "宝石" in goodName or "丹" in goodName or "玄晶" in goodName \
        or "铁镐" in goodName or "云龙剑" in goodName or "金蛇剑" in goodName \
        or "扫荡" in goodName:
            return False
        else:
            return True
        
    def __loadSellPack(self,msg):
        if msg.get('items') is not None:
            for good in msg.get('items'):
                if self.__goodIsForSell(good.get("name")):
                    self.__sellPack.append(good.get("id"))

    def __loadNpc(self,msg):
        if self.__npcName is not None and self.__npcId is None :
            for npc in msg.get("items"):
                if type(npc) is dict and self.__npcName in npc.get('name'):
                    self.__npcId = npc.get('id')
                    break
        
    def __load(self,msg):
        if type(msg) is dict and msg.get("type")=="items":
            self.__loadNpc(msg)
        if type(msg) is dict and msg.get("dialog") == "pack" :
            self.__loadSellPack(msg)

    def __close(self):
        self.isOpen = False
        self.__isStart = False
        self.__sellPack = []
    
    def open(self):
        self.isOpen = True
        if self.__isStart is False:
            self.__isStart = True
            return utils.getFlows("杂货铺")
    
    def __sellflows(self):
        flows = []
        for goodId in self.__sellPack:
            flows.append("sell 1 "+goodId+" to "+self.__npcId)
        return flows
        
    def mathineDo(self,msg):
        print(str(self.toDict()))
        self.__load(msg)
        if self.__npcId is not None and self.__sellPack != []:
            flows = self.__sellflows()
            self.__close()
            return flows
            
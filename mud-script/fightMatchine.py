# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 16:40:07 2018

@author: dk
"""

class FightMathine():
    def __init__(self,name):
        self.__name = name
        self.__enemy = []
        self.__body = []
        self.__enemyIsGet = False
        self.isOpen = False
        self.__isFighting = False
    
    def open(self):
        self.isOpen = True
        print("figth is been open")

    def __loadNpc(self,npcDict):
        if type(npcDict) is dict and npcDict.get("name") is not None \
            and "尸体" not in npcDict.get("name") \
            and self.__name not in npcDict.get("name") \
            and npcDict.get("id") is not None:
            self.__enemy.append(npcDict.get("id"))
            self.__enemyIsGet = True
    
    def __removeNpc(self,msg):
        if msg.get('id') is not None and msg.get('id') in self.__enemy:
            self.__enemy.remove(msg.get('id'))

    def __setFigthIsEnd(self):
        self.__isFighting = False
        
    def __loadBody(self,bodyDict):
        if (bodyDict.get("name") is not None) and ("尸体" in bodyDict.get("name")):
            self.__body.append(bodyDict.get('id'))
            
    def __loadState(self,msg):
        if "你要攻击谁" in msg:
            self.__setFigthIsEnd()
            
    def __load(self,msg):
        if type(msg) is dict and msg.get("items") is not None:
            for npcDict in msg.get("items"):
                self.__loadNpc(npcDict)
        if type(msg) is dict and msg.get('type') == "itemremove":
            self.__removeNpc(msg)
        if type(msg) is dict and msg.get('type') == "itemadd":
            self.__loadBody(msg)
        if type(msg) is dict and msg.get('type') == "combat" and  msg.get('end') == 1:
            self.__setFigthIsEnd()
        if type(msg) is str:
            self.__loadState(msg)

    def mathineDo(self,msg):
        self.__load(msg)
        if self.__isFighting:
            if self.__body:
                return ['get all from '+self.__body.pop()]
        else:
            if self.__enemy:
                self.__isFighting = True
                return ['kill '+self.__enemy.pop()]
            else:
                if self.__enemyIsGet:
                    self.isOpen = False
                    self.__enemyIsGet = False
        return None

        
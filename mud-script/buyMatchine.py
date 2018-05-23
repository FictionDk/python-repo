# -*- coding: utf-8 -*-
import mudUtils as utils

class BuyMatchine():
	def __init__(self,shopname,shopkeeper,goodname):
		self.__shopname = shopname
		self.__shopkeeper = shopkeeper
		self.__keeperid = None
		self.__goodname = goodname
		self.__goodid = None
	    self.isOpen = False
	    self.__goodIsLoad = False
        self.__isStart = False

    def open(self):
        self.isOpen = True
        if self.__isStart is False:
            self.__isStart = True
            return utils.getFlows(self.__shopname)

    def __loadSellPack(self,msg):
        if msg.get('items') is not None:
            for good in msg.get('items'):
            	if self.__goodname in good.get("name")
            		self.__goodid = good.get("id")
            		break
            self.__goodIsLoad = True

    def __loadNpc(msg):
        if self.__shopkeeper is not None and self.__keeperid is None :
            for npc in msg.get("items"):
                if type(npc) is dict and self.__shopkeeper in npc.get('name'):
                    self.__keeperid = npc.get('id')
                    break    	

    def __close(self):
        self.isOpen = False
        self.__isStart = False
        self.__goodIsLoad = False

    def load(self,msg):
        if type(msg) is dict and msg.get("type")=="items":
            self.__loadNpc(msg)
        if type(msg) is dict and msg.get("dialog") == "pack" :
            self.__loadSellPack(msg)

    def mathineDo(self,msg):
        self.__load(msg)
        if self.__goodIsLoad is True:
        	self.__close()
        	return None
        if self.__keeperid is not None and self.__goodid is not None:
            flows = ['buy 1'+self.__goodid+" from "+self.__keeperid]
            self.__close()
            return flows
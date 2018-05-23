# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 14:28:59 2018

@author: dk
"""

import mudUtils as utils
from bs4 import BeautifulSoup
import mudLogs as logger
import time
from mudClient import MudClient
from mudTask import TaskMachine,TaskStatus
from mineTaskMatchine import MineTaskMatchine

class Good():
    def __init__(self,name,gid,count):
        self.name = name
        self.gid = gid
        self.count = count

class DailyTaskMachine(TaskMachine):
    
    def __init__(self,name,status):
        self.name = name
        self.npcName,self.flows = self.__setTasker()
        self.status = status
        self.goods = []
        
        self.taskIsOver = False
        self.npcId = {"id":None,"isGet":False}
        self.pushNpc = {"id":None,"getting":False,"isGet":False}
        self.taskGood = {'name':None,'id':None,'buyying':False,'isBuy':False}
        self.taskIsPush = False
        self.goodsLoopList = self.__setGoodsLoopList()
        self.shopGoodList = []
        self.currentLoop = -1
        self.taskCount = 0
        self.giveUp = {"begin":False,"move":False,"do":False,"finish":False}
 
    def __setGoodsLoopList(self):
        goodLoopList = []
        goodLoopList.append({'name':'醉仙楼','person':'店小二','done':False, \
        'id':'','isList':False})
        goodLoopList.append({'name':'杂货铺','person':'杨永福','done':False,\
        'id':'','isList':False})
        goodLoopList.append({'name':'铁匠铺','person':'铁匠','done':False, \
        'id':'','isList':False})
        goodLoopList.append({'name':'医药铺','person':'平一指','done':False, \
        'id':'','isList':False})
        return goodLoopList
    
    def __setTasker(self):
        npcName,flowName = "",""
        if self.name == ("闻人晓" or "闻人雪"):
            npcName = "静心"
            flowName = "峨眉学艺2"
        elif self.name == ("醉书生" or "闻人博"):
            npcName = "岳不群"
            flowName = "华山派-客厅"
        elif self.name == "闻人泰":
            npcName = "武馆教习"
            flowName = "武馆"
        return npcName,flowName
 
    def __matchineDo(self,msg):
        if self.taskIsOver:
            print("task is over")
            return
        if self.currentLoop > 3 and self.giveUp['begin'] is False:
            logger.info("...give up this Task...")
            self.status = TaskStatus.DOING                                        
            self.giveUp['begin'] = True
            return
        if self.pushNpc.get('id') is not None and self.pushNpc.get('isGet') is False:
            self.status = TaskStatus.DOING
            self.pushNpc['isGet'] = True
            logger.info("pushNpc:"+str(self.pushNpc))
            return
        if self.taskGood.get('isBuy') is True and self.pushNpc.get('id') is None \
            and self.pushNpc.get('getting') is False:
            logger.info("taskGood:["+str(self.taskGood)+"] is Buy")
            self.pushNpc['getting'] = True
            self.status = TaskStatus.DOING
            return
        if self.giveUp.get('begin') is False \
            and self.goodsLoopList[self.currentLoop].get('id') != '' \
            and self.taskGood.get('name') is not None \
            and self.taskGood.get('buyying') is False:
            self.status = TaskStatus.DOING
            logger.info("searchLoop:"+str(self.goodsLoopList[self.currentLoop]) \
                        +" \n loopNum:"+str(self.currentLoop))
            return
        if self.taskGood.get('name') is not None and self.currentLoop == -1:
            self.status = TaskStatus.DOING
            self.currentLoop = 0
            logger.info("Task Good:"+str(self.taskGood))
            return
        if self.npcId.get("id") is not None and self.npcId.get("isGet") is False:
            self.status = TaskStatus.DOING
            self.npcId['isGet'] = True
            logger.info("NPC:"+self.npcName+"|"+str(self.npcId)+" has been get.")
        if self.giveUp.get('begin') is True and self.giveUp.get('move') is False:
            self.status = TaskStatus.DOING
            self.giveUp['move'] = True
        if self.giveUp.get('do') is False and self.pushNpc.get("id") is not None:
            self.status = TaskStatus.DOING
            self.giveUp['do'] = True

    def __selfRest(self):
        self.status = TaskStatus.LOCK
        self.taskIsOver = False
        self.npcId = {"id":None,"isGet":False}
        self.pushNpc = {"id":None,"getting":False,"isGet":False}
        self.taskGood = {'name':None,'id':None,'buyying':False,'isBuy':False}
        self.taskIsPush = False
        self.shopGoodList = []
        self.currentLoop = -1
        self.giveUp = {"begin":False,"move":False,"do":False,"finish":False}
        self.goodsLoopList = self.__setGoodsLoopList()
    
    def __initTask(self):
        return utils.getFlows(self.flows)
    
    def doTask(self,msg):
        if self.status is TaskStatus.END:
            return None
        if self.status is TaskStatus.STARTING:
            self.status = TaskStatus.LOCK
            return self.__initTask()
        self.__load(msg)
        self.__matchineDo(msg)
        if self.taskIsOver and self.status is not TaskStatus.END:
            self.__selfRest()
            return self.__initTask()
        if self.status is TaskStatus.LOCK or self.status is TaskStatus.END:
            return None
        if self.npcId.get("id") is not None and  self.npcId['isGet'] is True \
                and self.taskGood.get('name') is None:
            flows = ["task sm "+self.npcId.get('id')]
            self.status = TaskStatus.LOCK
            return flows
        if  self.taskGood.get('name') is not None \
            and self.currentLoop != -1 \
            and self.taskGood.get('isBuy') is False \
            and self.giveUp.get('begin') is False:
            if self.taskGood.get('id') is not None and self.taskGood.get('isBuy') is False:
                self.status = TaskStatus.LOCK
                self.taskGood['buyying'] = True
                logger.info("Buyying ="+str(self.currentLoop)+ \
                "||"+str(self.goodsLoopList[self.currentLoop]))
                return ["buy 1 "+self.taskGood.get('id')+" from " \
                        +self.goodsLoopList[self.currentLoop].get('id')]
            currentSearch = self.goodsLoopList[self.currentLoop]
            if currentSearch.get('done') is False:
                self.status = TaskStatus.LOCK
                return utils.getFlows(currentSearch.get('name'))
            elif currentSearch.get('id') != "" and currentSearch.get('isList') is False:
                self.status = TaskStatus.LOCK
                self.goodsLoopList[self.currentLoop]['isList'] = True
                return ['list '+currentSearch.get('id')]
        if self.taskGood.get('isBuy') is True and self.pushNpc.get('id') is None \
            and self.pushNpc.get('getting') is True:
            self.status = TaskStatus.LOCK
            return utils.getFlows(self.flows)
        if self.pushNpc.get('id') is not None and self.pushNpc.get('isGet') is True \
            and self.giveUp.get('begin') is False:
            self.status = TaskStatus.LOCK
            self.taskIsPush = True
            return ['task sm '+self.pushNpc.get('id')+' give '+self.taskGood.get('id')]
        if self.giveUp.get('begin') is True and self.giveUp.get('move') is False \
            and self.giveUp.get('do') is False:
            self.status = TaskStatus.LOCK
            return utils.getFlows(self.flows)
        if self.giveUp.get('do') is True and self.pushNpc.get("id") is not None:
            self.status = TaskStatus.LOCK
            return ['task sm '+self.pushNpc.get('id')+' giveup']
    
    #load data and change self status
    def __load(self,msg):
        if type(msg) is dict and msg.get("type") == "itemadd":
            self.__addNpcId(msg)
        if (type(msg) is dict and msg.get("type") == "items"):
            self.__getNpcId(msg)
        if type(msg) is dict and msg.get("type") == "dialog" and \
                  msg.get("dialog") == "pack":
            self.__getPackGoods(msg)
        if type(msg) is dict and msg.get('type') == "dialog" and \
                  msg.get("dialog") == "list":
            self.__updateShopGoodList(msg)
        if type(msg) is str and self.taskGood.get('name') is None:
            self.__getTaskGood(msg)
        if type(msg) is str:
            self.__checkTask(msg)
    
    def __getTaskGood(self,msg):
        if self.npcName and "对你说道" in msg:
            soup = BeautifulSoup(msg,"html.parser")
            goodName = None
            for label in self.__getTaskGoodLabel():
                goodName = soup.find(label)
                if goodName != None:
                    self.taskGood['name'] = str(goodName)
                    break;
                   
    def __getPackGoods(self,msg):
        if msg.get("items") is not None:
            for good in msg.get("items"):
                mygood = Good(good.get("name"),good.get("id"),good.get("count"))
                self.goods.append(mygood)
        if self.taskGood.get('name') is not None and msg.get('name') is not None \
            and self.taskGood.get('name') in msg.get('name'):
            self.taskGood['id'] = msg.get('id')
            self.taskGood['isBuy'] = True

    def __addNpcId(self,npc):
        if npc.get("name") is not None \
            and self.npcName in npc.get("name"):
            self.npcId["id"] = npc.get("id")
            
    def __getNpcId(self,msg):
        for npc in msg.get("items"):
            if type(npc) is dict:
                name = npc.get("name")
                if self.npcName in name and self.pushNpc.get('getting') is False \
                    and self.giveUp.get('move') is False:
                    self.npcId["id"] = npc.get("id")
                    break
                if self.npcName in name and (self.pushNpc.get('getting') is True \
                    or self.giveUp.get('move') is True):
                    self.pushNpc["id"] = npc.get("id")
                    break
                if self.taskGood.get('name') is not None \
                    and self.taskGood.get('id') is None \
                    and self.giveUp.get('begin') is False \
                    and self.goodsLoopList[self.currentLoop].get('person') in name:
                    self.goodsLoopList[self.currentLoop]['done'] = True
                    self.goodsLoopList[self.currentLoop]['id'] = npc.get('id')
                    break
    
    #get task good id
    def __updateShopGoodList(self,msg):
        for sellGood in msg.get('selllist'):
            if self.taskGood.get('name') in sellGood.get('name'):
                self.taskGood['id'] = sellGood.get('id')
                break
        if self.taskGood['id'] is None:
            self.currentLoop = self.currentLoop + 1
            self.status = TaskStatus.DOING
                
    # Get task goods in msg's label
    def __getTaskGoodLabel(self):
        return ['hig','wht']
    
    # check good is or not in pack
    def __checkPack(self):
        for good in self.goods:
            if good.name == self.taskGood:
                return True
        return  
    
    #check task is over
    def __checkTask(self,msg):
        if self.npcName and "孺子可教" in msg:
            self.taskIsOver = True
            self.status = TaskStatus.LOCK
        elif self.npcName and "先去休息吧" in msg:
            self.taskIsOver = True
            self.status = TaskStatus.LOCK
        if self.npcName and  "你先去休息一下吧" in msg:
            self.status = TaskStatus.END
            self.taskIsOver = True

def doCommond(mudRole,flows):
    if flows is None:
        return None
    for commond in flows:
        logger.info(mudRole.name+": do ["+commond+"]")
        mudRole.doCommond(commond)
        time.sleep(0.5)

def test():
    name = "韦晓宝"
    auth,socket_url = utils.getRoleConfig(name)
    mud = MudClient(auth,socket_url)
    mud.login()
    #taskMatchine = LearnTaskMatchine(name,TaskStatus.STARTING)
    mineTask = MineTaskMatchine(name,TaskStatus.STARTING)
    dailyTask = DailyTaskMachine(name,TaskStatus.STARTING)
    for i in range(2000):
        value = mud.flush()
        msg,flag = logger.info(value)
        flows = dailyTask.doTask(msg)
        if dailyTask.status is TaskStatus.END:
            flows = mineTask.doTask(msg)
        doCommond(mud,flows)
    mud.close()
    logger.close()

#test()

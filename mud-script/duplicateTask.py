# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:26:50 2018

@author: dk
"""

from mudTask import TaskMachine,TaskStatus
import mudUtils as utils
import mudLogs as logger
from mudClient import MudClient
from mineTaskMatchine import MineTaskMatchine
from fightMatchine import FightMathine
import time
from sellMatchine import SellMatchine

class DuplicateTask(TaskMachine):
    def __init__(self,name,status,dupName):
        self.name = name
        self.status = status
        self.dupName = dupName
        self.commonIndex = 0
        self.commonIsBegin = False
        self.figthIsStart = False
        self.commonList = utils.getFlows(self.dupName)
        self.fightMathine = FightMathine(name)
        self.sellMathine = SellMatchine(name)
        self.isSell = False
        self.room = ""

    def __loadRoom(self,msg):
        if type(msg) is dict and msg.get('type') == "room":
            self.room = msg.get('name')

    def __loadState(self,msg):
        if type(msg) is str and "精力不够" in msg:
            self.status = TaskStatus.OVER
        
    def __load(self,msg):
        self.__loadRoom(msg)
        self.__loadState(msg)
        
    def doTask(self,msg,i):
        if self.status is TaskStatus.END:
            return None
        self.__load(msg)
        if self.dupName == "dupOne":
            return self.__doDupOneTask(msg)
        if self.dupName == "dupBY":
            return self.__doDupBYTask(msg)

    def __doDupBYTask(self,msg):
        if self.commonIndex >= 8:
            if self.isSell is False:
                self.isSell = True
                return self.sellMathine.open()
            elif self.isSell and self.sellMathine.isOpen:
                return self.sellMathine.mathineDo(msg)
            elif self.isSell and self.sellMathine.isOpen is False:
                self.commonIndex = 0
                self.isSell = False
            #self.status = TaskStatus.OVER
            return None
        if self.commonIsBegin is False:
            commond = self.commonList[self.commonIndex]
            if self.commonIndex in (1,2):
                self.commonIsBegin = True
            else:
                self.commonIndex += 1
            return [commond]
        else:
           if "副本区域" in self.room:
               if self.figthIsStart:
                   if self.fightMathine.isOpen:
                       return self.fightMathine.mathineDo(msg)
                   else:
                       self.commonIndex += 1
                       self.commonIsBegin = False
                       self.figthIsStart = False
                       return None
               else:
                  self.figthIsStart = True
                  self.fightMathine.open()
                    

    def __doDupOneTask(self,msg):
        if self.commonIndex >= 9:
            if self.isSell is False:
                self.isSell = True
                return self.sellMathine.open()
            elif self.isSell and self.sellMathine.isOpen:
                return self.sellMathine.mathineDo(msg)
            elif self.isSell and self.sellMathine.isOpen is False:
                self.commonIndex = 0
                self.isSell = False
            return None
        if self.commonIsBegin is False:
            commond = self.commonList[self.commonIndex]
            if self.commonIndex in (1,2,3,5,6):
                self.commonIsBegin = True
            else:
                self.commonIndex += 1
            return [commond]
        else:
            if "流氓巷" in self.room:
                if self.figthIsStart:
                    if self.fightMathine.isOpen:
                        return self.fightMathine.mathineDo(msg)
                    else:
                        self.commonIndex += 1
                        self.commonIsBegin = False
                        self.figthIsStart = False
                        return None
                else:
                    self.figthIsStart = True
                    self.fightMathine.open()

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
    name = "韦晓宝"
    auth,socket_url = utils.getRoleConfig(name)
    mud = MudClient(auth,socket_url)
    mud.login()
    signinTaskIsOver = False
    #dupOne  dupBY
    dupMatchine = DuplicateTask(name,TaskStatus.STARTING,"dupBY")
    mineTask = MineTaskMatchine(name,TaskStatus.STARTING)
    for i in range (11000):
        value = mud.flush()
        msg,flag = logger.info(value)
        flows = dupMatchine.doTask(msg,i)
        if dupMatchine.status is TaskStatus.OVER:
            flows = mineTask.doTask(msg)
            if signinTaskIsOver is False :
                flows.append('taskover signin')
                signinTaskIsOver = True
        doCommond(mud,flows)
    mud.close()
    logger.close()

#test()

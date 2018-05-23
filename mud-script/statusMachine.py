# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 16:42:22 2018

状态机:
    name:用户名,
    wa:挖矿指数,
    pot:个人潜能pot,
    hp:血量
    mp:内力

@author: dk
"""
from enum import Enum
from dailyTaskMatchine import DailyTaskMachine

class StatusEnum(Enum):
    wa = "挖矿"
    fuben3 = "副本3"
    liaoshang = "疗伤"
    dazuo = "打坐"
    renwu = "师门任务"
    end = "断开连接"
    learning = "学习中"
    fighting = "战斗中"
    moveing = "移动中"

class StatusMachine(object):
    
    def __init__(self,name):
        self.name = name
        self.hp = 0
        self.hp_max = 0
        self.mp = 0
        self.mp_max = 0
        self.wa = 0
        self.pot = 0
        self.jingli = 0
        self.swordId = ""
        self.waId = ""
        self.state = ""
        self.nextState = ""
        self.room = ""
        self.daliy = DailyTaskMachine(self.name)
    
    #处理返回的数据    
    def load(self,info,flag):
        if flag:
            self.__loadJson(info)
    
    #处理json数据
    def __loadJson(self,info):
        if info.get("type") == "msg" and \
                   info.get("uid") == "mjta16f220f":
            self.__updateWa(info)
        elif info.get("type") == "msg" and \
                   info.get("name") == "醉书生" and \
                           info.get("content") == "end":
            self.nextState = StatusEnum.end
        elif info.get("type") == "itemadd" and \
                     self.name in info.get("name"):
            self.__updateSelf(info)
        elif info.get("type") == "dialog" and \
                     info.get("dialog") is "score":
            self.__update(info)
        elif info.get("type") == "room":
            self.room = info.get("name")    
    
    #更新个人状态
    def __updateSelf(self,info):
        self.hp = info.get("hp")
        self.hp_max = info.get("max_hp")
        self.hp = info.get("mp")
        self.hp = info.get("max_mp")
        self.jingli = info.get("jingli")
        self.pot = info.get("pot")
        
    #更新挖矿指数    
    def __updateWa(self,info):
        try:
            if "挖矿指南结束了!!!!!!!!!!" in info.get("content"):
                self.wa = 0
            else:
                self.wa = int(info.get("content"))
            print("更新挖矿指数为:%d"%self.wa)
        except :
            print("update minning Error")
    
    '''
    根据当前状态判断下一步做什么  
    返回需要执行的命令流(如果不需要做什么就为空)
    '''      
    def machineDo(self,msg):
        return self.daliy.doTask(msg)

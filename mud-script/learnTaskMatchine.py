# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 19:39:05 2018

@author: dk
"""
from mudTask import TaskMachine,TaskStatus
import mudUtils as utils
import mudLogs as logger
from mudClient import MudClient
import time
from mineTaskMatchine import MineTaskMatchine

class LearnTaskMatchine(TaskMachine):
    def __init__(self,name,status):
        self.name = name
        self.status = status
        self.master = {"name":None,"id":None}
        self.__setMasterName()
        self.skillList = self.__getSkillList()

    def __setMasterName(self):
        if self.name == "闻人博":
            self.master['name'] = "高根明"
        elif self.name == "闻人晓":
            self.master['name'] = "周芷若"
        elif self.name == "闻人泰":
            self.master['name'] = "武馆教习"
        elif self.name == "醉书生":
            self.master['name'] = "风清扬"
    
    def __getInitFlows(self):
        flowName = ""
        if self.name == "醉书生":
            flowName = "华山派-落雁峰" 
        elif self.name == "闻人晓":
            flowName = "峨眉派-小屋"
        elif self.name == "闻人泰":
            flowName = "武馆"
        return flowName   
        
    def __getSkillList(self):
        skillList = ["unarmed","force","dodge","parry","sword","literate"]
        if self.name == "闻人泰":
            skillList.remove("literate")
            skillList.append("throwing")
        elif self.name == "闻人晓":
            skillList.append("zhutianbu")
            skillList.append("jiuyinbaiguzhao")
            skillList.append("linjizhuang")
            skillList.append("huifengjian")
            skillList.reverse()
        elif self.name == "闻人雪":
            skillList.append("jindingzhang")
            skillList.append("emeixinfa")
        elif self.name == "醉书生":
            skillList.clear()
            skillList.append("sword")
            skillList.append("kuangfengkuaijian")
        return skillList

    def __loadMaster(self,msg):
        if self.master.get("name") is not None \
            and self.master.get("id") is None :
            for npc in msg.get("items"):
                if type(npc) is dict and self.master.get('name') in npc.get('name'):
                    self.master['id'] = npc.get('id')
                    self.status = TaskStatus.DOING
                    break

    def __loadStatus(self,msg):
        if type(msg) is str and ("无法领会" or "无法学习" or "不输你师父" or "不会这个技能")in msg:
            self.status = TaskStatus.DOING
        if type(msg) is dict and msg.get('type') == 'state' \
            and msg.get('state') == None:
            self.status = TaskStatus.DOING
    
    def __reLoadMaster(self,msg):
        if (msg.get("name") is not None) and (self.master.get('name') in msg.get("name")) \
           and msg.get('id') is not None:
            self.master['id'] = msg.get('id')
            self.status = TaskStatus.DOING
        
    def __load(self,msg):
        if self.status is TaskStatus.LOCK \
        and type(msg) is dict and msg.get("type") == "items":
            self.__loadMaster(msg)
        if self.status is TaskStatus.LOCK:
            self.__loadStatus(msg)
        if type(msg) is dict and msg.get("type") == "itemadd":
            self.__reLoadMaster(msg)

    def doTask(self,msg):
        self.__load(msg)
        if self.status is (TaskStatus.LOCK or TaskStatus.END or TaskStatus.OVER):
            return None
        if self.status is TaskStatus.STARTING:
            self.status = TaskStatus.LOCK
            return utils.getFlows(self.__getInitFlows())
        if self.status is TaskStatus.DOING:
            if self.skillList:
                skill = self.skillList.pop()
                self.status = TaskStatus.LOCK
                return ["xue "+skill+" from "+self.master.get('id')]
            else:
                self.status = TaskStatus.OVER

def doCommond(mudRole,flows):
    if flows is None:
        return None
    for commond in flows:
        logger.info(mudRole.name+": do ["+commond+"]")
        mudRole.doCommond(commond)
        time.sleep(1)

def main():
    name = "闻人晓"
    auth,socket_url = utils.getRoleConfig(name)
    mud = MudClient(auth,socket_url)
    mud.login()
    taskMatchine = LearnTaskMatchine(name,TaskStatus.STARTING)
    mineTask = MineTaskMatchine(name,TaskStatus.STARTING)
    tag = True
    while tag:
        value = mud.flush()
        msg,flag = logger.info(value)
        flows = taskMatchine.doTask(msg)
        if taskMatchine.status is TaskStatus.OVER:
            flows = mineTask.doTask(msg)
            tag = False
        doCommond(mud,flows)
        
    for i in range(20):
        value = mud.flush()
        logger.info(value)
    
    mud.close()
    logger.close()

main()
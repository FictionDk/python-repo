# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 21:24:06 2018

@author: dk
"""
from mudTask import TaskMachine,TaskStatus
import mudUtils as utils

class MineTaskMatchine(TaskMachine):
    def __init__(self,name,status):
        self.name = name
        self.status = status
        self.mineArr = False
    
    def __loadRoom(self,msg):
        if msg.get('path') == 'yz/kuang':
            self.status = TaskStatus.DOING
            self.mineArr = True
    
    def __load(self,msg):
        if self.status is TaskStatus.LOCK and type(msg) is dict \
            and msg.get('type') == "room":
            self.__loadRoom(msg)
    
    def doTask(self,msg):
        self.__load(msg)
        if self.status is (TaskStatus.LOCK or TaskStatus.END):
            return None
        if self.status is TaskStatus.STARTING:
            self.status = TaskStatus.LOCK
            return utils.getFlows('矿山')
        if self.status is TaskStatus.DOING and self.mineArr is True:
            self.status = TaskStatus.END
            return ['wa']
    
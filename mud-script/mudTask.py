# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 19:21:33 2018

@author: dk
"""

from enum import Enum

class TaskStatus(Enum):
    STARTING = "starting"
    LOCK = "lock"
    DOING = "doing"
    END = "end"
    OVER = "over"

class TaskMachine():
    def __init__(self,status):
        self.status = status
    
    def doTask(self):
        return None
    
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 17:04:50 2018

@author: dk
"""
import mudUtils as utils
from bs4 import BeautifulSoup
import mudLogs as logger
import time
from mudClient import MudClient
from mudTask import TaskMachine,TaskStatus
from mineTaskMatchine import MineTaskMatchine
from dailyTaskMatchine import DailyTaskMachine
from duplicateTask import DuplicateTask
from goodUseMatchine import GoodUseMatchine

def main():

    name = "闻人晓"
    auth,socket_url = utils.getRoleConfig(name)
    mud = MudClient(auth,socket_url)
    mud.login()
    mineTask = MineTaskMatchine(name,TaskStatus.STARTING)
    dailyTask = DailyTaskMachine(name,TaskStatus.STARTING)
    goodUseMatchine = GoodUseMatchine("养精丹",None)
    dupMatchine = DuplicateTask(name,TaskStatus.STARTING,"dupBY")
    signinTaskIsOver = False
    goodUse = False

    isDoingDailyTask = True
    isDoingDuplicateTask = True
    while isDoingDailyTask:
        value = mud.flush()
        msg,flag = logger.info(value)
        flows = dailyTask.doTask(msg)
        doCommond(mud,flows)
        if dailyTask.status is TaskStatus.END:
            isDoingDailyTask = False
            print(isDoingDailyTask)

    flows = goodUseMatchine.open()
    doCommond(mud,flows)
    for i in range (8):
        value = mud.flush()
        msg,flag = logger.info(value)
        if goodUseMatchine.isOpen is True:
            flows = goodUseMatchine.mathineDo(msg)
        doCommond(mud,flows)

    while isDoingDuplicateTask:
        value = mud.flush()
        msg,flag = logger.info(value)
        flows = dupMatchine.doTask(msg,0)
        if dupMatchine.status is TaskStatus.OVER:
            isDoingDuplicateTask = False
            print(isDoingDailyTask)
        doCommond(mud,flows)
        
    doCommond(mud,['taskover signin'])

    for i in range(30):
        value = mud.flush()
        msg,flag = logger.info(value)
        flows = mineTask.doTask(msg)
        doCommond(mud,flows)


    mud.close()
    logger.close()


def doCommond(mudRole,flows):
    if flows is None:
        return None
    for commond in flows:
        if commond is None:
            return None
        logger.info(mudRole.name+": do ["+commond+"]")
        mudRole.doCommond(commond)
        time.sleep(0.5)

main()
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 17:01:08 2018

角色信息类

需要记录的信息包括:
    当前状态
    血量/最大血量
    内力/最大内力
    精力
    潜能
(可选:所处位置,背包内情况,可用动作)
    
@author: dk
"""

class Role():
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
        self.renwu = 20
    
    def update():
        print("do update")
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 14:19:17 2018

mud操作工具类

@author: dk
"""
__roleDicts = {}
__flows = {}

# 基础配置信息获取
def getRoleConfig(name):
    if __roleDicts:
        auth = __roleDicts.get(name)
    else:
        __roleConfigInit()
        auth = __roleDicts.get(name)
    socket_url = "ws://120.78.75.229:25631/"
    print("name is %s"%name)
    if name == "韦晓宝":
        socket_url = "ws://47.106.8.121:25631/"
    print("socket_url is %s"%socket_url)
    return auth,socket_url   

# 工作流获取
def getFlows(name):
    if __flows:
        return __flows.get(name)
    else:
        __flowCollectionInit()
        return __flows.get(name)
    
# 初始化角色配置
def __roleConfigInit():
    inFile = open("./conf/roles.txt",encoding="utf-8")
    lines = inFile.readlines()
    for line in lines:
        line = line.strip('\n')
        config = line.split('|')
        userConfig = {}
        userConfig['rName'] = config[0]
        userConfig['user'] = config[1]
        userConfig['pwd'] = config[2]
        userConfig['uid'] = config[3]
        __roleDicts[config[0]] = userConfig

#工作流集合初始化
def __flowCollectionInit():
    infile = open("./conf/flows.txt",encoding="utf-8")
    lines = infile.readlines()
    for line in lines:
        line = line.strip('\n')
        line = line.split('|')
        flowName = line[0]
        del(line[0])
        __flows[flowName] = line

#获取当前角色待学习的列表
def getSkillList(name):
    skillList = ["unarmed","force","dodge","parry","sword","literate"]
    if name == "闻人泰":
        skillList.append("sword")
        skillList.append("throwing")
    elif name == "闻人晓":
        #skillList.append("emeixinfa")
        skillList.append("zhutianbu")
        skillList.append("jindingzhang")
    elif name == "闻人雪":
        skillList.append("sword")
        skillList.append("emeixinfa")
    return skillList

#获取当前角色需要学习的师傅名字
def getMasterName(name):
    masterName = ""
    if name == "闻人泰":
        masterName = "94vh1989fb9"
    elif name == "闻人晓":
        masterName = "acmu1cb99cd"
    elif name == "闻人博":
        masterName = "94vh1989fb9"
    elif name == "闻人雪":
        masterName = "zbiq1cb999e"
    return masterName 

def test():
    flows = getFlows("杂货铺")
    print("1:flow is %s"%str(flows))
    flows = getFlows("杂货铺")
    print("2:flow is %s"%str(flows))
    
test()
    
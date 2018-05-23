
class DailyTask():
    def __init__(self,name,status):
        self.name = name
        self.npcName,
        self.flows = self.__setTasker()
        self.goodsLoopList = self.__setGoodsLoopList()

        self.status = status
        self.goods = []
        self.taskIsOver = False
        self.npcId = {"id":None,"isGet":False}
        self.pushNpc = {"id":None,"getting":False,"isGet":False}
        self.taskGood = {'name':None,'id':None,'buyying':False,'isBuy':False}
        self.taskIsPush = False
        self.shopGoodList = []
        self.currentLoop = -1
        self.taskCount = 0
        self.giveUp = {"begin":False,"move":False,"do":False,"finish":False}

    def doTask(self,msg):
        self.__load(msg)
        self.__matchineDo(msg)

    def __matchineDo(self,msg):
    	if taskGood.get("name") is not None:
    		

    
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

    # Get task goods in msg's label
    def __getTaskGoodLabel(self):
        return ['hig','wht']

    def __getTaskGood(self,msg):
	    if self.npcName and "对你说道" in msg:
	        soup = BeautifulSoup(msg,"html.parser")
	        goodName = None
	        for label in self.__getTaskGoodLabel():
	            goodName = soup.find(label)
	            if goodName != None:
	                self.taskGood['name'] = str(goodName)
	                break;

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

    def __load(self,msg):
        if type(msg) is str and self.taskGood.get('name') is None:
            self.__getTaskGood(msg)
        if type(msg) is str:
            self.__checkTask(msg)
        if type(msg) is dict and msg.get("type") == "itemadd":
            self.__addNpcId(msg)
        if type(msg) is dict and msg.get("type") == "items":
            self.__getNpcId(msg)
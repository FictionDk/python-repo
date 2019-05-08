# -*- coding: utf-8 -*-
class Fly(object):
    def __init__(self,fromdis,todis,airline):
        self.fromdis = fromdis
        self.todis = todis
        self.airline = airline

    def setValue(self,departingtime,price,content,savedate):
        self.departingtime = departingtime
        self.price = price
        self.content = content
        self.savedate = savedate

    def toDict(self):
        objDict = {}
        objDict['fromdis'] = self.fromdis
        objDict['todis'] = self.todis
        objDict['departingtime'] = self.departingtime
        objDict['price'] = self.price
        objDict['content'] = self.content
        objDict['airline'] = self.airline
        return objDict

    def toTuple(self):
        flyTuple = (self.airline,self.savedate,self.fromdis,self.todis,self.departingtime,self.price,self.content)
        return flyTuple

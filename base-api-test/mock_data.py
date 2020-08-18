# -*- coding: utf-8 -*-
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
PERSON_DIR = os.path.join(WORK_DIR,"random")
sys.path.append(PERSON_DIR)
from core import RandomPerson
from core import RandomTime

class MockData():

    def __init__(self):
        self.index = 8
        self.person = RandomPerson()
        self.timer = RandomTime()

    def _random_datetime(self, min_day = 0, max_day = 7):
        rand_data = self.timer.random_date(max_day = max_day)
        return self.timer.random_datetime(rand_date = rand_data).strftime('%Y-%m-%d %H:%M:%S')

    def random_data(self,index):
        if index % self.index == 0:
            return self.build_consumable()
        elif index % self.index == 1:
            return self.build_register()
        elif index % self.index == 2:
            return self.build_bodycheck()
        elif index % self.index == 3:
            return self.build_bloodcheck()
        elif index % self.index == 4:
            return self.build_collection()
        elif index % self.index == 5:
            return self.build_storerecord()
        elif index % self.index == 6:
            return self.build_logadd()
        elif index % self.index == 7:
            return self.build_new()
        else:
            return None,None

    def build_new(self):
        name,sex,idcardId,area,birth = self.person.get_person()
        if "boy" is sex:
            sex_int = 1
        else:
            sex_int = 2
        dat = {
            "donatorName": name,
            "idcardId": idcardId,
            "sex": sex_int,
            "idcardAddress": area,
            "nation": "汉",
            "birthday": birth,
            "phoneNumber": "18074706701",
            "homeAddress": area,
            "township": "",
            "village": "",
            "diseasehistory": "",
            "registeDate": self._random_datetime()
        }
        return "donator/new",dat

    def build_register(self):
        name,sex,idcardId,area,birth = self.person.get_person()
        dat = {}
        dat["donatorName"] = name
        dat["idcardId"] = idcardId
        dat["operatorName"] = "黎先聪"
        dat["operatorDate"] = self._random_datetime()
        return "donator/registe",dat

    def build_bodycheck(self):
        name,sex,idcardId,area,birth = self.person.get_person()
        dat = {
            "donatorName": name,
            "idCardId": idcardId,
            "bodyWeight": 59.1,
            "bodyTemperature": 36.6,
            "sphygmus": 72.0,
            "systolicPressure": 17.3,
            "diastolicPressure": 10.5,
            "heartLungs": True,
            "liverspleen": True,
            "skin": True,
            "limbs": True,
            "remark": "",
            "checkResult": "ok",
            "checkperson": "黄凌璘",
            "createTime": self._random_datetime()
        }
        return "bodycheck/save",dat

    def build_bloodcheck(self):
        name,sex,idcardId,area,birth = self.person.get_person()
        dat = {
            "donatorName": name,
            "idCardId": idcardId,
            "checkResult": "ok",
            "hemoglobin": "%E2%89%A5120",
            "plasmaProteins": "%E2%89%A550",
            "bloodProportion": "ok",
            "hbsag": "negative",
            "syphilis": "negative",
            "alt": "%E2%89%A425u",
            "antiHcv": "negative",
            "antinHiv": "negative",
            "checkTime": self._random_datetime(),
            "checkPerson": "韦生民"
        }
        return "bloodcheck/save",dat

    def build_storerecord(self):
        name,sex,idcardId,area,birth = self.person.get_person()
        dat = [{
            "donatorName": name,
            "idCardId": idcardId,
            "packageId": "25319P00199422",
            "plasmaAmount": 600,
            "collectResult": "ok",
            "optName": "韦家庚",
            "operation": "入库",
            "remark": None
        }]
        return "storerecord/save",dat

    def build_collection(self):
        name,sex,idcardId,area,birth = self.person.get_person()
        dat = {
            "donatorName": name,
            "idCardId": idcardId,
            "collectVolum": 600,
            "collectinfo": "{\"circulationNumber\":29,\"CycleTimes\": 2}",
            "collectResult": "ok",
            "operatorName": "黄英",
            "collectDate": self._random_datetime(),
            "Remark": ""
        }
        return "plasmacollect/save",dat

    def build_consumable(self):
        dat = {}
        dat["consumableName"] = "HBsAg"
        dat["consumableNum"] = "1"
        dat["consumableUnit"] = "孔"
        dat["consumableBatch"] = "1"
        dat["availableDate"] = "2022-10"
        dat["operation"] = "入库"
        return "consumstore/save",dat

    def build_logadd(self):
        dat = {
            "operateDate": self._random_datetime(),
            "operatorName": "",
            "content": "付款",
            "remark": ""
        }
        return "log/add",dat

def main():
    mock = MockData()
    print(mock.build_new())

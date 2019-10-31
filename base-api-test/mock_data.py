# -*- coding: utf-8 -*-

class MockData():

    def __init__(self):
        self.index = 8;

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
        dat = {
            "deptNo": "4501240455",
            "donatorName": "蒙凤川",
            "idcardId": "452127197610200361",
            "sex": 2,
            "idcardAddress": "广西马山县白山镇内学村巴朝屯74号",
            "nation": "壮",
            "birthday": "1976-10-20",
            "phoneNumber": "18074706701",
            "homeAddress": "广西马山县白山镇内学村巴朝屯74号",
            "township": "",
            "village": "",
            "diseasehistory": "",
            "registeDate": "2019-09-01 00:00:00"
        }
        return "donator/new",dat

    def build_register(self):
        dat = {}
        dat["donatorName"] = "唐梅兰"
        dat["idcardId"] = "45252419640712148X"
        dat["operatorName"] = "黎先聪"
        dat["operatorDate"] = "2019-08-27 00:00:00"
        return "donator/registe",dat

    def build_bodycheck(self):
        dat = {
            "donatorName": "覃刚宇",
            "idCardId": "452702198402213678",
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
            "createTime": "2019-08-26 00:00:00"
        }
        return "bodycheck/save",dat

    def build_bloodcheck(self):
        dat = {
            "donatorName": "石青平",
            "idCardId": "452730196312284735",
            "checkResult": "ok",
            "hemoglobin": "%E2%89%A5120",
            "plasmaProteins": "%E2%89%A550",
            "bloodProportion": "ok",
            "hbsag": "negative",
            "syphilis": "negative",
            "alt": "%E2%89%A425u",
            "antiHcv": "negative",
            "antinHiv": "negative",
            "checkTime": "2019-09-01 00:00:00",
            "checkPerson": "韦生民"
        }
        return "bloodcheck/save",dat

    def build_storerecord(self):
        dat = [{
            "donatorName": "黄炳海",
            "idCardId": "452730196703300536",
            "packageId": "25319P00199422",
            "plasmaAmount": 600,
            "collectResult": "ok",
            "optName": "韦家庚",
            "operation": "入库",
            "remark": None
        }]
        return "storerecord/save",dat

    def build_collection(self):
        dat = {
            "donatorName": "马玉梅",
            "idCardId": "452627198206201129",
            "collectVolum": 600,
            "collectinfo": "{\"circulationNumber\":19,\"CycleTimes\": 2}",
            "collectResult": "ok",
            "operatorName": "黄英",
            "collectDate": "2019-08-12 00:00:00",
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
            "operateDate": "2019-08-31 15:36:22",
            "operatorName": "",
            "content": "付款",
            "remark": ""
        }
        return "log/add",dat
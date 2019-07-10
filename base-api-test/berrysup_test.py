# -*- coding: utf-8 -*-
import requests

def get_dat(typ):
    if "consumstore" == typ:
        return build_consumable()
    else:
        return None

def build_consumable():
    dat = {}
    dat["consumableName"] = "HBsAg"
    dat["consumableNum"] = "1"
    dat["consumableUnit"] = "孔"
    dat["consumableBatch"] = "1"
    dat["availableDate"] = "2022-10"
    # dat["operation"] = "入库"
    return dat

def get_url():
    return "http://192.168.110.47:8006/api/"

def build_header():
    return "19053009","6f55d4d1-b2b2-4cb6-9125-14c3ac05d01c"

def dat_post(typ,dat):
    url = get_url() + typ + "/save"
    code,key = build_header()
    header = {}
    header["stationcode"] = code
    header["secretkey"] = key
    r = requests.post(url,json=dat,headers=header)
    return req_result(r)

def req_result(re):
    rdict = re.json()
    result = {}
    result["status"] = rdict.get("status")
    if not re.ok:
        result["error"] = rdict.get("error")
        result["exception"] = rdict.get("exception")
        result["message"] = rdict.get("message")
    else:
        result["status"] = "200"
        result["body"] = rdict
    return result

def consumstore_mock():
    typ = "consumstore"
    consumstore_dat = get_dat(typ)
    dat_post(typ,consumstore_dat)

if __name__ == "__main__":
    for i in range(4000):
        consumstore_mock()

# coding: UTF-8

import requests
import json

store_uri = "http://192.168.110.84:9003/api/blood/store"

store = '{\
    "facilityCode":"110248",\
    "reportTime":"2018-11-08 15:30:00",\
    "data":[{\
        "comClass":"02",\
        "comCategory":"38",\
        "bloodGroup":"A+",\
        "count":20,\
        "volume":200.0\
    }]\
}'

resp = requests.post(url=store_uri,json=json.loads(store));


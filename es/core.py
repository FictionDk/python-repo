# -*- coding: utf-8 -*-

import time
import json
from elasticsearch import Elasticsearch

class ESConnect():
    def __init__(self, host="192.168.110.13",port=9200):
        self.es = Elasticsearch(['%s:%s'%(host,str(port))])

    def recive_log(self, content_str, index_name="optlog", content_name="CoreOptLog"):
        content_json = json.loads(content_str)
        if 'createTime' in content_json:
            time_arr = time.strptime(content_json['createTime'], "%Y-%m-%d %H:%M:%S")
            second = int(time.mktime(time_arr))
        else:
            second = int(time.time())

        body = {
            "name": content_name,
            "content": content_str,
            "optUuid": content_json.get('optUuid',None),
            "optTitle": content_json['optTitle'],
            "optText": content_json['optText'],
            "second": second
        }

        if self.es.indices.exists(index_name) :
            print("索引存在")
        else:
            print("索引不存在")
            self.es.indices.create(index=index_name)

        self.es.index(index=index_name, body=body)

def test():
    content_str = '{"optIp":"172.17.0.1","optTitle":"core","optType":"GET","optText":"查看角色",\
    "optResult":"OK","createTime":"2019-10-17 15:29:00","optContent":{"roleType":"管理"}}'

    es_until = ESConnect()
    es_until.recive_log(content_str=content_str, index_name='contry')
    print("Data insert sucess.")

# test()
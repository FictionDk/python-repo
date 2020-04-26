# -*- coding: utf-8 -*-

import json
import os
import time

# 获取文件全路径名称
def _get_full_filename(filename,dir):
    dir_name = os.path.join(os.getcwd(),dir)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_name = os.path.join(dir_name,filename)
    # 确保被创建
    if not os.path.isfile(full_name):
        with open(full_name,'a+',encoding="utf-8") as f:
            f.close()
    return full_name

'''
获取配置列表:

url: 连接地址
port: 连接端口
username: 用户名
password: 用户密码
vhost: 工作空间
'''
def get_config():
    config_name = _get_full_filename("pro.conf",'conf')

    with open(config_name,'r+',encoding="utf-8") as f:
        config_str = f.readline()
        config_json = {}

        if len(config_str) > 0:
            config_json = json.loads(config_str)
        else:
            raise EnvironmentError
        return config_json

def save_log(msg):
    datastr = time.strftime("%Y-%m-%d", time.localtime())
    logfile_name = _get_full_filename(datastr + ".log",'logs')
    body = filter_body(msg)
    if body is not None:
        with open(logfile_name,'a+',encoding="utf-8") as f:
            f.write(filter_body(msg) + "\n")

def filter_body(msg):
    content = {}
    try:
        msg = json.loads(msg)
        msg = json.loads(msg["message"])
        content["req_time"] = msg["@timestamp"]
        content["remote_ip"] = msg["@fields"]["remote_addr"]
        content["req_method"] = msg["@fields"]["request_method"]
        content["req_body"] = msg["@fields"]["request_body"]
        content["req_path"] = msg["@fields"]["request"]
        content["status"] = msg["@fields"]["status"]
        content["uid"] = msg["@fields"]["uid"]
    except json.JSONDecodeError as e:
        print(str(msg),"JSONDecodeError:",str(e))
        return None
    else:
        return json.dumps(content)

def _save_test():
    save_log("json")

def _filter_test():
    body = '{"@timestamp":"16/Jan/2020:19:52:57 +0800","@fields":{"remote_addr":"176.58.124.134",\
        "remote_user": "","request_method":"","request_body":"","http_referrer": "","request": "\bw<W 0\\",\
        "status":"400"}}'
    result = filter_body(body)
    print(result)

if __name__ == "__main__":
    _filter_test()

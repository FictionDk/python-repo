# -*- coding: utf-8 -*-

import json
import os

# 获取文件全路径名称
def _get_full_filename(filename):
    dir_name = os.path.join(os.getcwd(),'conf')
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
    config_name = _get_full_filename("pro.conf")

    with open(config_name,'r+',encoding="utf-8") as f:
        config_str = f.readline()
        config_json = {}

        if len(config_str) > 0:
            config_json = json.loads(config_str)
        else:
            raise EnvironmentError
        return config_json

def test():
    print(get_config())

if __name__ == "__main__":
    test()
# -*- coding: utf-8 -*-

import os,sys,time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# 打包后的环境
if getattr(sys, 'frozen', False):
    BASE_DIR = BUNDLE_DIR

def _get_config():
    with open(os.path.join(BASE_DIR,"pda.conf"),"r",encoding="utf-8") as f:
        arr = f.read().splitlines()
        return arr[0], arr[1].split(',')

def pda_reg_post():
    url, pda_arr = _get_config()
    for pda_no in pda_arr:
        header,body = {"serialNo": pda_no}, {"auto": True}
        r = requests.post(url=url+"/bus/pda/register", json=body, headers=header)
        if r.ok:
            print("设备 %s 注册成功" % pda_no)
        else:
            print("设备 %s 注册失败" % pda_no)
    time.sleep(5)

if __name__ == "__main__":
    pda_reg_post()
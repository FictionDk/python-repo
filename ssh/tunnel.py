# -*- coding: utf-8 -*-

import re
from sshtunnel import SSHTunnelForwarder
import time

def ssh_1(ip, port, usr, pwd, keeplive):
    server = SSHTunnelForwarder(ssh_address_or_host=(ip,port),
    ssh_username=usr,
    ssh_password=pwd,
    local_bind_address=('127.0.0.1',8100),
    remote_bind_address=('127.0.0.1',80))
    server.start()
    print("start started")
    time.sleep(keeplive)
    print("start stopped")
    server.stop()

def _get_config():
    result = {}
    with open("tunnel.conf","r",encoding="utf-8") as f:
        arr = f.read().splitlines()
        result['keeplive'] = arr[0].replace('\n','')
        result['usr'] = arr[1]
        result['pwd'] = arr[2]
        result['ip'] = arr[3]
        result['port'] = arr[4]
    return result

if __name__ == "__main__":
    conf = _get_config()
    print(conf)
    ssh_1(conf['ip'],int(conf['port']),conf['usr'],conf['pwd'],int(conf['keeplive']))

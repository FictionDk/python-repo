# -*- coding: utf-8 -*-

from sshtunnel import SSHTunnelForwarder
import time

# 214.254.2.78:30020
def ssh_1(ip, port, usr, pwd, keeplive):
    print(f"{ip}:{port} starting")
    server = SSHTunnelForwarder(ssh_address_or_host=(ip,port),
        ssh_pkey="/Users/fictio/.ssh/id_rsa",
        local_bind_address=('127.0.0.1',30020),
        remote_bind_address=('214.254.2.78',30020))
    server.start()
    print(f"{ip} started success")
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
    ssh_1(conf['ip'],int(conf['port']),conf['usr'],conf['pwd'],int(conf['keeplive']))

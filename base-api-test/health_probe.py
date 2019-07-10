# -*- coding: utf-8 -*-
import requests
import os
import time

def server_uri():
    return "http://127.0.0.1:8006/health"
    # return "http://192.168.110.47:8006/health"

def server_is_up():
    is_ok = False
    try:
        re = requests.get(server_uri())
        if re.ok and re.json()["status"] == "UP":
            is_ok = True
    except Exception as e:
        print("ERROR==>",str(e))
    return is_ok

def server_restart():
    try:
        os.system("docker restart berrysupervise")
    except Exception as e:
        print("ERROR==>",str(e))

def main():
    while True:
        time.sleep(30)
        if not server_is_up():
            server_restart()

if __name__ == "__main__":
    main()

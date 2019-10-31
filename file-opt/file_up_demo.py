# -*- coding: utf-8 -*-

import requests
import json
import file_utils

def json_test():
    a = {"name":"go","version":"3.1"}
    print("a",a.get("name"))
    b = json.dumps(a)
    print(b,"|type is",type(b))
    c = json.loads(b)
    print(c,"|type is",type(c))

    file_fullname = file_utils.get_full_filename("type.json","yoyo")
    with open(file_fullname,'a+',encoding="utf-8") as f:
        f.write(b + "\n")

def upload_file():
    url = "http://192.168.110.13"
    file_fullname = file_utils.get_full_filename("type.json","yoyo")
    data = None
    files = {"xxxx":open(file_fullname, "rb").read()}

    r = requests.post(url + '/upload',data,files=files)
    path = url + "/file"
    is_ok = False
    if r.ok:
        rj = json.loads(r.content)
        if rj["code"] is 200:
            path += rj["data"]["fileurl"]
            is_ok = True
        else:
            print("upload filed, result: %s." % str(rj))
    else:
        print("Connect failed,code is %s. content is %s" % (str(r),str(r.content)))
    if is_ok:
        print(path)

if __name__ == '__main__':
    json_test()
    upload_file()

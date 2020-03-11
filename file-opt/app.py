# -*- coding: utf-8 -*-

import requests
import json
import file_utils
import time

def __acess_file_type():
    return ['png','jpg','bmp','jpeg']

def upload_file(url,name,file_fullname):
    files = {name:open(file_fullname, "rb").read()}

    r = requests.post(url + '/upload',None,files=files)
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
    return is_ok,path

def main():
    url = "https://plasma.stpass.com"
    file_list = file_utils.get_filename_in_dir('assert')
    print(file_list)
    for file_name in file_list:
        if file_utils.check_file_type(file_name,__acess_file_type()):
            file_fullname = file_utils.get_full_filename('assert',file_name)
            is_ok,path = upload_file(url,file_name,file_fullname)
            log_content = "[" + file_name + "] [" + path + "] [" + str(is_ok) + "]"
            file_utils.save_log('logs',log_content)

if __name__ == '__main__':
    main()
    time.sleep(5)

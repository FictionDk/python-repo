import requests
import json

def test():
    a = {"name":"go","version":"3.1"}
    print("a",a.get("name"))
    b = json.dumps(a)
    print(b,"|type is",type(b))
    c = json.loads(b)
    print(c,"|type is",type(c))
    pass

def upload_file():
    url = "http://192.168.110.48/upload"
    file_name = "E:\\home\\yuncloud\\Lenka - Blue Skies.mp3"
    data = None
    files = {"Skies.mp3" : open(file_name, "rb").read()}
    r = requests.post(url,data,files=files)
    path = "http://192.168.110.48/file"
    is_ok = False
    if r.ok :
        rj = json.loads(r.content)
        if rj["code"] is 200: 
            path += rj["data"]["fileurl"]
            is_ok = True
        else: 
            print("upload filed, result: %s." % str(rj))
    else:
        print("Connect failed,code is %s." % str(r))
    if is_ok:
        print(path)

if __name__ == '__main__':
    upload_file()
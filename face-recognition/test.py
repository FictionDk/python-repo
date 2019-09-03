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
    # url = "http://192.168.110.48/upload"
    url = "http://plasma.stpass.com"
    # file_name = "E:\\home\\yuncloud\\Lenka - Blue Skies.mp3"
    file_name = "D:\\Resource\\baiducloud\\IMG_20141213_111656_HDR.jpg"
    data = None
    files = {"IMG_20141213_111656_HDR.jpg":open(file_name, "rb").read()}
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
    upload_file()

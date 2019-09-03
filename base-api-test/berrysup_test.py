# -*- coding: utf-8 -*-
import requests
import time
from mock_data import MockData

failed_count = {}

def get_url():
    return "http://127.0.0.1:8006/api/"

def build_header():
    return "19053009","6f55d4d1-b2b2-4cb6-9125-14c3ac05d01c"

def dat_post(path,dat):
    url = get_url() + path
    code,key = build_header()
    header = {}
    header["stationcode"] = code
    header["secretkey"] = key
    r = requests.post(url,json=dat,headers=header)
    return r

def req_result(re):
    rdict = re.json()
    result = {}
    result["status"] = rdict.get("status")
    if not re.ok:
        result["error"] = rdict.get("error")
        result["exception"] = rdict.get("exception")
        result["message"] = rdict.get("message")
    else:
        result["status"] = "200"
        result["body"] = rdict
    return result

def mock_test(index):
    global failed_count
    mock = MockData()
    path,dat = mock.random_data(index)
    result = dat_post(path,dat)
    if not result.ok:
        if path in failed_count:
            failed_count[path] += 1
        else:
            failed_count[path] = 1
        req_result(result)

def main():
    start_time = time.time()
    count = 0
    for i in range(80):
        mock_test(i)
        count += 1
    end_time = time.time()
    print("Time consuming: %f s, Count: %d" % ((end_time - start_time),count))
    print("Failed Count: ")
    print(failed_count)

if __name__ == "__main__":
    main()
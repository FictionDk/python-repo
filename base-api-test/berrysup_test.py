# -*- coding: utf-8 -*-
import requests
import time
from mock_data import MockData

failed_count = {}

failed_detail = []

def get_url():
    return "http://192.168.110.13:8006/api/"
    # return "http://127.0.0.1:8006/api/"

def build_header():
    return "4501240455","fc2785bf-6a24-411b-932a-545688c83143"

def dat_post(path,dat):
    url = get_url() + path
    code,key = build_header()
    header = {}
    header["stationcode"] = code
    header["secretkey"] = key
    r = requests.post(url,json=dat,headers=header)
    return r

def req_result(re):
    global failed_detail
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
    failed_detail.append(result)
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
    for i in range(8):
        mock_test(i)
        count += 1
    end_time = time.time()
    print("Time consuming: %f s, Count: %d" % ((end_time - start_time),count))
    print("Failed Count: %s " % str(failed_count))
    for msg in failed_detail:
        print(msg)

if __name__ == "__main__":
    main()

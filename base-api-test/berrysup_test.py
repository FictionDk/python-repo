# -*- coding: utf-8 -*-
import requests
import time
import random
from mock_data import MockData

failed_count = {}

failed_detail = []

def get_url():
    return "http://192.168.110.13:8006/api/"
    # return "http://127.0.0.1:8006/api/"

def build_header():
    random_num = random.randint(0,5)
    headers = [
        ["4510230181","a60453ef-9e26-4db1-9524-3b4c5d5a073d", "平果光明"],
        ["4501240455","fc2785bf-6a24-411b-932a-545688c83143", "马山莱士"],
        ["4506030308","8e46d11d-271f-48fc-bc8e-d685f738d40d", "防城港泰邦"],
        ["4512260185","dfa6da98-916e-4d66-8c4b-e2d358be05b9", "环江泰邦"],
        ["4511021076","20a8087d-216e-467c-8c88-edba717bb250", "贺州华兰"],
        ["4501240455","fc2785bf-6a24-411b-932a-545688c83143", "马山莱士"]
    ]
    return headers[random_num]

def dat_post(path,dat):
    url = get_url() + path
    code,key,name = build_header()
    header = {}
    header["stationcode"] = code
    header["secretkey"] = key
    r = requests.post(url,json=dat,headers=header)
    return r,code

def req_result(re, fac_id):
    global failed_detail
    rdict = re.json()
    result = {}
    result["status"] = rdict.get("status")
    if not re.ok:
        result["error"] = rdict.get("error")
        result["exception"] = rdict.get("exception")
        result["message"] = rdict.get("message")
        result["dept"] = fac_id
    else:
        result["status"] = "200"
        result["body"] = rdict
    failed_detail.append(result)
    return result

def mock_test(index):
    global failed_count
    mock = MockData()
    path,dat = mock.random_data(index)
    result,fac_id = dat_post(path,dat)
    if not result.ok:
        if path in failed_count:
            failed_count[path] += 1
        else:
            failed_count[path] = 1
        req_result(result, fac_id)

def main():
    start_time = time.time()
    count = 0
    cycles = 10
    for i in range(cycles * 8):
        mock_test(i)
        count += 1
        if count % 100 == 0:
            c_end_time = time.time()
            print("%f s, count is: %d" %((c_end_time - start_time), count))
    end_time = time.time()
    print("Time consuming: %f s, Count: %d" % ((end_time - start_time),count))
    print("Failed Count: %s " % str(failed_count))
    for msg in failed_detail:
        print(msg)

if __name__ == "__main__":
    main()
    time.sleep(8)

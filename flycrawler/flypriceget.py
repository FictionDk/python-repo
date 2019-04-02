# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
from datetime import date,datetime,timedelta
from flyDB import FlyDB
import time
from fly import Fly
'''
机票价格爬虫
'''
def request(url):
    result = requests.get(url)
    if result.status_code == 200:
        return result.content
    else:
        print("请求失败." + str(result.status_code))
        return False

def process(content,fly):
    result = []
    soup = BeautifulSoup(content,"html.parser")
    rows = soup.find_all(class_="cssRadio row3")
    while len(rows) > 0:
        row = rows.pop()
        if row is not None:
            label = row.contents[1]
            labelDict = label.attrs
            departingtime = labelDict['data-departingtime']
            value = labelDict['value']
            label = row.contents[3]
            labelDict = label.attrs
            price = labelDict['data-amount']
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            fly.setValue(departingtime,price,value,now)
            if float(price) < 3000:
                result.append(fly.toTuple())
        else:
            print("请求失败,价格行为空")
        print(json.dumps(fly.toDict()))
    return result

def conf(date,fromdis,todis):
    url = 'https://beta.cebupacificair.com/Flight/InternalSelect?'
    param = 'o1=' + fromdis + "&d1=" + todis + "&o2=&d2=&dd1=" + date + "&p=&ADT=1&CHD=0&INF=0&s=true&mon=true"
    fly = Fly(fromdis,todis,"cebu")
    return url + param,fly

def test():
    day = date(2020,2,1)
    url,fly = conf(day.strftime('%Y-%m-%d'),'MNL','CEB')
    result = request(url)
    rows = process(result,fly)
    print("================================")
    for row in rows:
        print(row)

# HKG,CEB,ILO,
def main():
    day = date(2019,2,1)
    for i in range(3):
        url,fly = conf(day.strftime('%Y-%m-%d'),'HKG','ILO')
        result = request(url)
        if result is False:
            print("获取数据失败")
            return
        rows = (process(result,fly))

        url,fly = conf(day.strftime('%Y-%m-%d'),'HKG','CEB')
        result = request(url)
        if result is False:
            print("获取数据失败")
            return
        rows.extend(process(result,fly))

        url,fly = conf(day.strftime('%Y-%m-%d'),'HKG','MNL')
        result = request(url)
        if result is False:
            print("获取数据失败")
            return
        rows.extend(process(result,fly))
        
        flyDB = FlyDB("mysql")
        flyDB.insertValue(rows)

        time.sleep(2)
        print("current date is %s ,flydate been Get" % day.strftime('%Y-%m-%d'))
        day = day + timedelta(days=1)

test()

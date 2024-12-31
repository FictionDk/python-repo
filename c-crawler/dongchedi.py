# -*- coding: utf-8 -*-
import requests

base = "https://www.dongchedi.com/motor/pc/car/rank_data?aid=1839&app_name=auto_web_pc"

def getSaleRanking(count:int, offset:int, month:str) -> any[bool, list]:
    r = requests.get(f'{base}&count={count}&offset={offset}&month={month}&rank_data_type=11')
    print(r.status_code)
    if r.ok:
        return True, r.json()['data']['list']
    else: 
        print(r.json())
        return False, None
    

def main():
    ok, rankList = getSaleRanking(20, 0, '202411')
    if ok == False:
        print(f'Get {base} faild')
        return
    for r in rankList:
        print(r)


if __name__ == "__main__":
    main()
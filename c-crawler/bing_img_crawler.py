# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time

def get_host():
    return 'bing.ioliu.cn'

def get_dir_path():
    # return 'E://home/pic//'
    return 'E://OneDrive//Pictures//'

def get_header():
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'host': get_host(),
        'Referer': 'https://' + get_host() + '/',
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/74.0.3729.169 Safari/537.36'
    }
    return headers

def get_img_list():
    img_list = []
    url = 'https://' + get_host() + '/?p=1'
    result = requests.get(url,headers=get_header())
    print("get_img_list = %s" % result)
    soup = BeautifulSoup(result.content,"html.parser")
    img_rows = soup.find_all(class_='card progressive')
    for img_row in img_rows:
        img = {}
        desc = img_row.find(class_='description')
        ori_url = img_row.find(class_='options').find(class_='ctrl download').attrs['href']
        img['name'] = str(desc.h3.string).split(' ')[0] + '.jpg'
        img['url'] = 'https://' + get_host() + ori_url
        img['time'] = str(desc.p.em.string)
        img_list.append(img)
        print(img.get('name') + '--' + img.get('url'))
    return img_list

def save_img(img):
    r = requests.get(img.get('url'))
    if r.ok:
        try:
            with open(get_dir_path() + img.get('name'), 'wb') as fb:
                fb.write(r.content)
                return True
        except Exception as err:
            print(err)
    else:
        print("Req failed %s" % str(r.content))
    return False

def log_save(msg,result):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    __fileName = "./log/bing_img_crawler.log"
    with open(__fileName,'a+',encoding='utf-8') as fb:
        fb.write(time_str + "--" + str(result) + '-- ' + str(msg) + '\n')
        fb.flush()

def save_img_list(img_list):
    for img in img_list:
        flag = save_img(img)
        log_save(img.get('name') + "|" + img.get('time'),flag)

def main():
    img_list = get_img_list()
    save_img_list(img_list)

if __name__ == "__main__":
    main()
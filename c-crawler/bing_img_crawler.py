# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = "logs"
PICS_DIR = "Pictures"
LOG_FILE = "bing_img_crawler.log"

# 打包后的环境
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
if getattr(sys, 'frozen', False):
    BASE_DIR = BUNDLE_DIR

def get_host():
    return 'bing.ioliu.cn'

def get_dir_path():
    return BASE_DIR
    # return 'D://Doc//OneDrive//Pictures//'
    # return 'E://OneDrive//Pictures//'

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
    result = requests.get(url, headers=get_header())
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
        time.sleep(1)
    return img_list

def save_img(img):
    r = requests.get(img.get('url'), headers=get_header())
    if r.ok:
        try:
            with open(get_full_filename(PICS_DIR,img.get('name')), 'wb') as fb:
                fb.write(r.content)
                return True
        except Exception as err:
            print(err)
    else:
        print("Req failed %s" % str(r.content))
    return False

# 获取文件全路径名称
def get_full_filename(dirname,filename):
    dir_name = os.path.join(BASE_DIR,dirname)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_name = os.path.join(dir_name,filename)
    # 确保被创建
    if not os.path.isfile(full_name):
        with open(full_name,'a+',encoding="utf-8") as f:
            f.close()
    return full_name


def log_save(msg,result):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    __fileName = get_full_filename(LOGS_DIR,LOG_FILE)
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

def test(url):
    save_img(url)

if __name__ == "__main__":
    main()
    time.sleep(1)
    # img = {}
    # img['url'] = 'https://bing.ioliu.cn/photo/MetamorphicRocks_ZH-CN9753251368?force=download'
    # img['name'] = '缅因州达马里斯科塔地区的佩马基德灯塔 (© Tom Whitney/Adobe Stock).jpg'
    #img['time'] = '2020-03-15 17:16:44'
    #test(img)

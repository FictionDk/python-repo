# -*- coding: utf-8 -*-

import os
from selenium import webdriver
from time import sleep

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = "logs"

'''
D:/Resource/chromedriver_win32/chromedriver.exe
下载地址
https://sites.google.com/chromium.org/driver/
'''
def _get_driver_path(own_machine=True):
    if own_machine:
        return os.path.join('D:',os.path.sep,'Resource','chromedriver_win32','chromedriver.exe')
    else:
        return os.path.join('E:',os.path.sep,'OneDrive')

def _get_snapshot_path(file_path):
    return os.path.join(BASE_DIR,LOGS_DIR,file_path)

def _build_browser(driver_path):
    browser = webdriver.Chrome(driver_path)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # 无头
    chrome_options.add_argument('--disable-gpu')  # 无GPU
    browser = webdriver.Chrome(driver_path, options=chrome_options)  # 构建一个chrome对象
    return browser

def test():
    ioliu_url = 'https://bing.ioliu.cn?p=1'
    driver_path = _get_driver_path()
    browser = _build_browser(driver_path)
    browser.get(ioliu_url)
    sleep(3)
    screenshot_path = _get_snapshot_path('b.png')
    browser.get_screenshot_as_file(screenshot_path)
    sleep(3)
    browser.quit()
    print("Finished")

test()

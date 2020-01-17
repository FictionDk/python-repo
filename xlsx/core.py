# -*- coding: utf-8 -*-

import openpyxl
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_pic_uri():
    return os.path.join('E:',os.path.sep,'OneDrive')

def _get_pic_files():
    path = _get_pic_uri()
    print(path)
    files = os.listdir(path)
    for i in range(len(files)):
        print(files[i])

def _get_full_filename(filename,dir):
    dir_name = os.path.join(os.getcwd(),dir)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_name = os.path.join(dir_name,filename)
    # 确保被创建
    if not os.path.isfile(full_name):
        with open(full_name,'a+',encoding="utf-8") as f:
            f.close()
    return full_name

def build_xlsx():
    xlsx_name = _get_full_filename("test.xlsx","docs")
    workbook = openpyxl.Workbook()
    workbook.save(xlsx_name)

def main():
    # _get_pic_files()
    build_xlsx()

if __name__ == '__main__':
    main()
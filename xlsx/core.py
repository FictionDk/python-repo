# -*- coding: utf-8 -*-

import openpyxl
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_pic_uri():
    return os.path.join('E:',os.path.sep,'OneDrive')

def _get_pic_files():
    path = _get_pic_uri()
    files = os.listdir(path)
    pic_files = []
    for i in range(len(files)):
        if _is_pic_file(files[i],path):
            pic_files.append(files[i])
    return pic_files

def _is_pic_file(filename,path):
    full_filename = os.path.join(path,filename)
    if os.path.isfile(full_filename) and 'Pictures' == filename[0:8]:
        return True
    else:
        return False

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

def _get_content():
    content = []

    old_path = _get_pic_uri()
    new_path = os.path.join(old_path,"Pictures")
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    pic_files = _get_pic_files()
    for pic in pic_files:
        pic_content = [os.path.join(old_path,pic),os.path.join(new_path,pic.replace('Pictures',''))]
        content.append(pic_content)

    return content

def build_xlsx():
    xlsx_name = _get_full_filename("test.xlsx","docs")
    workbook = openpyxl.Workbook()
    ws = workbook.active

    pics = _get_content()
    for pic in pics:
        ws.append(pic)
    workbook.save(xlsx_name)

def files_move():
    xlsx_name = _get_full_filename("test.xlsx","docs")
    workbook = openpyxl.load_workbook(xlsx_name,read_only=True)
    ws = workbook.active

    rows = ws.rows
    for row in rows:
        print(row[0].value,"->",row[1].value)
        try:
            shutil.move(row[0].value,row[1].value)
        except FileNotFoundError as e:
            print("FileNotFoundError")

def main():
    # build_xlsx()
    files_move()

if __name__ == '__main__':
    main()
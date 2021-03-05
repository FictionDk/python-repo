# -*- coding: utf-8 -*-
import os
import time
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# 打包后的环境
if getattr(sys, 'frozen', False):
    BASE_DIR = BUNDLE_DIR

class ArgsNotNull(RuntimeError):
    pass

def get_full_filename(directory,filename=None):
    '''获取当前执行目录下的指定路径下的文件名
    Args:
        filename: 文件名,可为空,返回文件夹全路径
        directory: 目录名称
    Returns:
        返回文件的全路径
    Raises:
        ArgsNotNull: 参数不能为空
    '''
    if directory is None:
        raise ArgsNotNull("directory can not be None")
    dir_name = os.path.join(BASE_DIR,directory)

    # 确保目录存在
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if filename is None:
        return dir_name
    full_name = os.path.join(dir_name,filename)
    # 确保文件存在
    if not os.path.isfile(full_name):
        with open(full_name,'a+',encoding="utf-8") as f:
            f.close()
    return full_name

def read_raw_datas():
    file_name = 'D:\\Resource\\RFID\\czxz210128.txt'
    result = []
    with open(file_name,'r',encoding="utf-8") as f:
        str_lines = f.readlines()
        for str_line in str_lines:
            str_arr = str_line.replace('\n','').split(',')
            if(str_arr[12] == 'true'):
                row = {}
                row['SID'] = str_arr[1]
                row['TID'] = str_arr[0]
                row['FL'] = str_arr[8]
                row['RE'] = str_arr[9]
                result.append(row)
    return result

def build_sql(m):
    sql = 'INSERT INTO tidmapping("serial_id", "tid", "flag", "remark", "vendor", "created_at") VALUES (SID, TID, FL, RE,'
    for k in m.keys():
        sql = sql.replace(k, m.get(k).replace('"','\''))
    sql = sql + '\'SOAP\',\'2021-01-28 21:00:00\');'
    return sql

def save_sql(sqls):
    file_name = get_full_filename("docs","mapping.sql")
    print(file_name)
    with open(file_name,'a+',encoding="utf-8") as f:
        for sql in sqls:
            f.write(sql + "\n")

def test():
    rows = read_raw_datas()
    sqls = []
    for row in rows:  # for row in rows[1:3]:
        sqls.append(build_sql(row))
    save_sql(sqls)

test()

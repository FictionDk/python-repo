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

def get_filename_in_dir(directory):
    '''获取当前执行目录下的指定路径下的文件名列表
    Args:
        directory: 目录名称

    Returns:
        返回文件的全路径
    '''
    dir_full_path = get_full_filename(directory)
    return os.listdir(dir_full_path)

def save_log(directory,message):
    '''在当前目录下的directory目录下的upload.log文件中记录日志
    Args:
        directory: 日志文件夹
        message: 日志内容

    Returns:
        返回文件的全路径
    '''
    logfile_name = get_full_filename(directory,'fileupload.log')
    datastr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(logfile_name,'a+',encoding="utf-8") as f:
        f.write(datastr + ": " + message + "\n")


def check_file_type(file_name,type_names):
    '''根据文件名判断的类型是否在 type_names 中
    Args:
        file_name: str类型,文件名称
        type_names: List类型, 小写的类型名称, 如['png','jpeg']

    Returns:
        True/False
    '''
    file_type = os.path.splitext(file_name)[-1][1:]
    return file_type.lower() in type_names

'''
D://Home//pythonspace//python-repo//face-recognition//assert
'''
def _get_pic_uri():
    return os.path.join('D:',os.path.sep,'Home','pythonspace','python-repo','face-recognition','assert')

def get_pic_filename(file_name):
    file_path = _get_pic_uri()
    return os.path.join(file_path,file_name)

def _get_workspace_path():
    return os.path.join('C:',os.path.sep, 'workspace', 'work-mkt', 'berry', 'berrynotify', 'src', 'main', 'java')

def _find_file(arg, dirname, files):
    for file in files:
        file_path = os.path.join(dirname, file)
        if os.path.isfile(file_path):
            print("%s"%file)

def test():
    base_path = _get_workspace_path()
    all_file_names = []
    for parent_dir, dir_names, file_names in os.walk(base_path, followlinks=False):
        all_file_names.extend(file_names)

    file_list_path = get_full_filename('yoyo', 'file_list.txt')
    for file in all_file_names:
        with open(file_list_path,'a+',encoding="utf-8") as f:
            f.write(file + "\n")

test()

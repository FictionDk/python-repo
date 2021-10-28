# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

def read(filepath):
    tube_lines = []
    with open(filepath,'r',encoding="utf-8") as f:
        return f.readlines()

def buid(tube_lines):
    srts = []
    index = 1
    for i,val in enumerate(tube_lines):
        if val[0:2].isdigit() and len(tube_lines) > i + 2:
            start_time = "00:" + val.replace('\n','') + ",000"
            end_time = "00:" + tube_lines[i+2].replace('\n','') + ",000"
            content = tube_lines[i+1].replace('\n','')
            srt = str(index) +'\n' + start_time + " --> " + end_time + '\n' + content + '\n'
            index += 1
            srts.append(srt)
    return srts

def save(srts,outpath):
    with open(outpath,'a+',encoding="utf-8") as f:
        for srt in srts:
            f.write(srt + '\n')

def main():
    filepath = get_full_filename('docs', 'test.txt')
    outpath = get_full_filename('docs', 'text.srt')
    tube_lines = read(filepath)
    srts = buid(tube_lines)
    print(srts)
    save(srts, outpath)

main()

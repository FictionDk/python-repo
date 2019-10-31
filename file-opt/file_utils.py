# -*- coding: utf-8 -*-

import os

# 在当前目录下的指定目录创建文件
# filename: 文件名
# directory: 指定目录
def get_full_filename(filename,directory):
    dir_name = os.path.join(os.getcwd(),directory)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_name = os.path.join(dir_name,filename)
    # 确保被创建
    if not os.path.isfile(full_name):
        with open(full_name,'a+',encoding="utf-8") as f:
            f.close()
    return full_name

from PIL import Image
import numpy as np
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _get_assert_path(filename = None):
    dir_name = os.path.join(BASE_DIR,'assert')
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if filename is None:
        return dir_name
    full_path = os.path.join(dir_name,filename)
    return full_path

def read_from_arr(name):
    full_path = _get_assert_path(name)
    arr = np.load(full_path)
    pil_image = Image.fromarray(arr)
    pil_image.show()

def get_npy_files():
    '''批量获取npy列表
    '''
    path = _get_assert_path()
    files = os.listdir(path)
    npys = []
    for i in range(len(files)):
        if _is_npy_file(files[i],path):
            npys.append(files[i])
    return pic_files

def _is_npy_file(filename,path):
    full_filename = os.path.join(path,filename)
    if os.path.isfile(full_filename):
        return True
    else:
        return False

# 结果检验
def result_show():
    print(get_npy_files())

result_show()

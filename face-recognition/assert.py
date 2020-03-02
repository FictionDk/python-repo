from PIL import Image
import numpy as np
import os

def _get_assert_path(filename):
    dir_name = os.path.join(os.getcwd(),'assert')
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_path = os.path.join(dir_name,filename)
    return full_path

def read_from_arr(name):
    full_path = _get_assert_path(name)
    arr = np.load(full_path)
    pil_image = Image.fromarray(arr)
    pil_image.show()

# 结果检验
def result_show():
    name = 'a_0.npy'
    read_from_arr(name)
    name = 'b_0.npy'
    read_from_arr(name)

result_show()

# -*- coding: utf-8 -*-
import os
from PIL import Image
import numpy as np

# 根据图片的url
def image_pixelate(image_url):
    return None

# 输入 image: 包含人脸照片
# 输出 人脸特征np数组
def image_to_arr(image):
    return np.array(image)

def read_image_from_file(filepath):
    pil_img = Image.open(filepath)
    return pil_img

def _get_image_path(filename):
    dir_name = os.path.join(os.getcwd(),'assert')
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_path = os.path.join(dir_name,filename)
    return full_path

def test():
    filepath = _get_image_path('a.png')
    pil_img = read_image_from_file(filepath)
    # pil_img.show()
    img_arr = image_to_arr(pil_img)
    print(img_arr)

test()

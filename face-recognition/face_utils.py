import os
import numpy as np
from PIL import Image
import requests
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_assert_path(filename):
    dir_name = os.path.join(BASE_DIR,'assert')
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    full_path = os.path.join(dir_name,filename)
    return full_path

def save_arr_to_file(arr,name):
    full_path = get_assert_path(name + '.npy')
    np.save(file=full_path,arr=arr)

def image_to_arr(image):
    return np.array(image)

def read_image_from_file(filepath):
    pil_img = Image.open(filepath).convert('RGB')
    return pil_img

def read_image_from_url(url):
    r = requests.get(url)
    img_file = r.content
    im = Image.open(io.BytesIO(img_file))
    im = im.convert('RGB')
    image_arr = np.array(im)
    return image_arr

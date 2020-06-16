import os
import numpy as np
from PIL import Image
import requests
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_assert_path(filename=None, pathname='assert'):
    '''获取静态文件目录路径,文件名为空时返回路径
    Args:
        filename 目录下文件名称
    Return:
        str, 返回文件全路路径,文件名为空时文件夹全路径
    '''
    dir_name = os.path.join(BASE_DIR,pathname)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if filename is None:
        return dir_name
    full_path = os.path.join(dir_name,filename)
    return full_path

def save_arr_to_file(arr,name):
    '''将npy数组存入文件
    Args:
        arr npy数组
        name npy保存文件名称
    '''
    full_path = get_assert_path(name + '.npy')
    np.save(file=full_path,arr=arr)

def image_to_arr(image):
    '''将二进制图片转换成npy数组
    Args:
        image 二进制图片文件
    '''
    return np.array(image)

def read_image_from_file(filepath):
    '''通过图片全路径读取文件,返回PIL二进制文件
    '''
    pil_img = Image.open(filepath).convert('RGB')
    return pil_img

def read_image_from_url(url):
    '''通过图片url获取图片内容
    Args:
        url strm图片网络存放路径
    Return:
        npy数组
    '''
    r = requests.get(url)
    img_file = r.content
    im = Image.open(io.BytesIO(img_file))
    im = im.convert('RGB')
    image_arr = np.array(im)
    return image_arr

def get_npy_list(batch_count = 100):
    '''批量获取npy列表
    '''
    path = get_assert_path()
    files = os.listdir(path)
    npy_list = []
    name_list = []
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(path,x)))
    for i in range(len(files)):
        print(files[i])
        if _is_npy_file(files[i],path):
            npy_list.append(np.load(get_assert_path(files[i])))
            name_list.append(files[i].replace('.npy',''))
    return npy_list,name_list

def identifaction_result_build(distance_list, face_name_list, threshold):
    '''返回身份认证结果
    Args:
        distance_list list, 人脸相似差距识别结果
        face_name_list list, 对应的人脸身份证id
        threshold float, 过滤阈值
    Returns:
        返回认证相似度大于threshold的结果,包括身份证号和相似度
    '''
    identifactions = []
    if len(distance_list) > 0 and len(distance_list) == len(face_name_list):
        for i,distance in enumerate(distance_list):
            prob = 1 - distance
            if prob > threshold:
                face_result = {}
                face_result['idcard_id'] = face_name_list[i]
                face_result['prob'] = prob
                identifactions.append(face_result)
    return identifactions

def livedetect_result(distance_list, min_faces=3, threshold=0.7):
    '''活体认证检验结果
    Args:
        distance_list: 人脸相似差距识别结果
        min_faces: 最小人脸数
        threshold: 相似度阈值
    '''
    if len(distance_list) > 0 and len(distance_list) > min_faces:
        for distance in distance_list:
            prob = 1 - distance
            if prob < threshold:
                return False
        return True
    return False

def _is_npy_file(filename,path):
    full_filename = os.path.join(path,filename)
    if os.path.isfile(full_filename) and '.npy' in filename:
        return True
    else:
        return False

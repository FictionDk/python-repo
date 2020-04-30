from PIL import Image
import numpy as np
import os
import requests
import time
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

failed_detail = []

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

def face_banding():
    global failed_detail 
    count = 0
    faces = _get_face_urls()
    start_time = time.time()
    for face in faces:
        r = requests.post(_get_post_url(),json=face)
        rdict = r.json()
        if rdict.get("code") == '0':
            print("%s banding sucess!" % face['idcard_id'])
            count += 1
        else:
            print("%s banding failed!" % face['idcard_id'])
            failed_detail.append(face)
    end_time = time.time()
    print("Time consuming: %f s, SuccessCount: %d, TotolCount: %d" % ((end_time - start_time),count,len(faces)))
    if len(failed_detail) > 0:
        print(failed_detail)

def _get_post_url():
    return "http://192.168.110.13:5001/face/binding"

def _get_face_urls():
    faces_file = _get_assert_path('fileupload.log')
    lines = None
    faces = []
    with open(faces_file,'r',encoding="utf-8") as f:
        lines = f.readlines()

    if lines is not None:
        for line in lines:
            face_name, face_url = _build_date_from_line(line)
            face = {}
            face['idcard_id'] = face_name.split('_')[0]
            face['face_img_url'] = face_url
            faces.append(face)
    return faces

def _build_date_from_line(line):
    results = line.split(' ')
    if len(results) == 5 and _date_symbol_clean(results[4]) == 'True':
        return _date_symbol_clean(results[2]), _date_symbol_clean(results[3])
    else:
        None, None

def _date_symbol_clean(date):
    return date.replace('[','').replace(']','').replace('\n', '').replace('\r', '')

# 结果检验
def result_show():
    print(face_banding())

face_banding()

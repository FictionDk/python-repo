# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
import requests
import face_recognition
from flask import Flask,jsonify,request
import io
import datetime

app = Flask(__name__)

"""
比对两张图片是否有人脸和相似度

:param url_1: 图片1url
:param url_2: 图片2url
:return: json
"""
@app.route('/face/compare',methods=['POST'])
def face_compare():
    request_data = request.get_json()
    url_old = ''
    url_new = ''
    result = {"status":"failed","msg":"参数缺少或错误"}
    if 'url_old' in request_data:
        url_old = request_data['url_old']
    if 'url_new' in request_data:
        url_new = request_data['url_new']
    print(url_old,"|",url_new)
    print("get url_old begin, ",url_old)
    a = datetime.datetime.now()

    if url_old is '' or url_new is '':
        return jsonify(result)

    image1_arr = getImage(url_old)
    face1_in_image = True
    face1_codes,face1_in_image = face_encoding(image1_arr,face1_in_image)

    if(not face1_in_image):
        result = {"result":"failed","msg":"no face in url_old"}
        return jsonify(result)

    b = datetime.datetime.now()
    print("get url_old end ,",url_old,"use time: ",str((b - a).seconds))
    print("get url_new begin, ",url_new)
    a = datetime.datetime.now()

    image2_arr = getImage(url_new)
    face2_in_image = True
    face2_codes,face2_in_image = face_encoding(image2_arr,face2_in_image)

    if(not face2_in_image):
        result = {"result":"failed","msg":"no face in url_new"}
        return jsonify(result)

    b = datetime.datetime.now()
    print("get url_new end, ",url_new,"use time: ",str((b - a).seconds))

    dis_result = face_recognition.face_distance(face2_codes,face1_codes[0])
    print(dis_result)
    result = {"result":"success","msg":"compare success","prob":str(1 - dis_result[0])}
    return jsonify(result)

"""
输入个人信息及人脸图片url,分割人脸保存ndarray并使用face_encoding获取特征码

:param url: 图片url
:param name: 姓名
:param idcardId: 身份证编号
:return: json
"""
@app.route('/face/encoding',methods=['POST'])
def face_image_encoding():
    request_data = request.get_json()
    url = ''
    name = ''
    idcardId = ''
    result = {"status":"failed","msg":"参数缺少或错误"}
    if 'url' in request_data:
        url = request_data['url']
    if 'name' in request_data:
        name = request_data['name']
    if 'idcardId' in request_data['idcardId']:
        idcardId = request_data['idcardId']

    print(url+"|"+name+"|"+idcardId)

    if url is None or name is None or idcardId is None:
        return jsonify(result)

    image_arr = getImage(url)
    face_locations = face_location(image_arr)
    if len(face_locations) is 0:
        result['msg'] = "照片中不存在人脸"
        return jsonify(result)
    if len(face_locations) is not 1:
        result['msg'] = "照片中存在多个人脸"
        return jsonify(result)

    face_im = face_image_get(image_arr,face_locations[0])
    fileName = 'face_npy\\'+name+"_"+idcardId+"_face.npy"
    np.save(file=fileName,arr=face_im)


# 人脸图片切割
def face_image_get(image,face_location):
    top,right,bottom,left = face_location
    return image[top:bottom,left:right]

# 输入图片url路径,获取np数组
def getImage(url):
    r = requests.get(url)
    img_file = r.content
    im = Image.open(io.BytesIO(img_file))
    image_arr = np.array(im)
    return image_arr

# 图片特征抽取
def face_encoding(image,face_in_image):
    face_encodings = face_recognition.face_encodings(image)
    if len(face_encodings) == 0:
        print("hot模式抽取图片人脸特征失败,启用cnn算法抽取")
        face_encodings = face_recognition.face_encodings(image,face_location(image))
        if len(face_encodings) == 0:
            face_in_image = False
    return face_encodings,face_in_image

# 获取人脸定位
def face_location(image):
    face_locations = face_recognition.face_locations(image)
    if(len(face_locations) == 0):
        print("hot模式定位图片人脸失败,启用cnn算法")
        face_locations = face_recognition.face_locations(image,number_of_times_to_upsample=1,model="cnn")
    return face_locations

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001)

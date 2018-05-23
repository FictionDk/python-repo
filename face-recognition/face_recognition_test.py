# -*- coding: utf-8 -*-

"""
Created on Fri Dec  8 09:26:40 2017

@author: dk
"""
import face_recognition
import numpy as np
from PIL import Image
from flask import Flask,jsonify,request,redirect
import requests
import io

ALLOWED_EXTENTIONS = {'png','jpg','jpeg','gif'}

app = Flask(__name__)


def allowd_file(filename):
    return '.' in filename and \
 filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENTIONS
             
@app.route('/face',methods=['GET','POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowd_file(file.filename):
            return detect_faces_in_image(file)
    return '''
    <!doctype html>
    <title>Is this a picture of refuser?</title>
    <h1>Upload a picture and see if it's a picture of refuse person!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

# 需求比对图片获取  /isPass?url=https://...
@app.route('/face/isPass',methods=['GET'])
def face_image_get():
    url = request.args.get('url')
    print("比对"+url+"是否通过")
    r = requests.get(url)
    img_file = r.content
    im = Image.open(io.BytesIO(img_file))
    image_arr = np.array(im)
    face_in_image = True
    face_codes,face_in_image = face_encoding(image_arr,face_in_image)
    if(not face_in_image):
        result = {"result":"failed","msg":"no face in image"}
    if len(face_codes) == 1:
        dis = is_hekui_face_in(face_codes)
        print(dis)
        result = {"result":"success","msg":"compare success","prob":str(1-dis[0])}
    else:
        result = {"result":"failed","msg":"mult face in image"}
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
        
    r = requests.get(url)
    img_file = r.content
    im = Image.open(io.BytesIO(img_file))
    image_arr = np.array(im)
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
    
    result["status"] = "success"
    result["msg"] = "save success"
    return jsonify(result)


def detect_faces_in_image(file):
    image = face_recognition.load_image_file(file)
    is_face_in_image = True
    #face_encodings = face_encoding(image,is_face_in_image)
    #face_location_print(image,face_location(image),)
    if(is_face_in_image):
        face_compare(face_recognition.face_encodings(image),image)
        result = {"face_name":"XXX","probobiliiity":"60"}
    else:
        result = {"msg":"no face in image"}
    return jsonify(result)

def is_hekui_face_in(face_encodings):
    face_hekui = np.load('face_npy\\face_hekui_1.npy')
    dis_result = face_recognition.face_distance(face_encodings,face_hekui)
    return dis_result

def face_compare(face_encodings,image):
    if(len(face_encodings)==0):
        face_encodings = face_recognition.face_encodings(image,face_location(image))
        if(len(face_encodings)==0):
            return False
    face_encoding = face_encodings[0]
    print(type(face_encoding))
    print(face_encoding)
    #print(face_encodings[0].shape)
    face_hekui = np.random.randn(128,1)
    face_hekui = np.load('face_npy\\face_hekui.npy')
    print(face_hekui)
    print(type(face_hekui))
    #face_model_one = np.load('face_npy\\face_model_one.npy')
    print(face_hekui.shape)
    dis_results_1 = face_recognition.face_distance(face_encodings,face_hekui)
    #dis_results_2 = face_recognition.face_distance(face_encodings,face_model_one)
    print(dis_results_1)
    #print(dis_results_2)

# 人脸分离并打印:
def face_location_print(image,face_locations):
    print("图片中人脸个数:{}".format(len(face_locations)))
    i = 0
    for face_location in face_locations:
        face_image = face_image_get(image,face_location)
        pil_image = Image.fromarray(face_image)
        #pil_image.show()
        face_image_save(pil_image,i)
        i += 1

# 人脸图片保存
def face_image_save(pil_image,i):
    pil_image.save("one_face.jpg")

# 人脸图片切割
def face_image_get(image,face_location):
    top,right,bottom,left = face_location
    return image[top:bottom,left:right]

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
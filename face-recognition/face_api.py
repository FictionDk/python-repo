# -*- coding: utf-8 -*-
from flask import Flask,jsonify,request
import face_utils
from core import FaceAccredit

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

    if url_old is '' or url_new is '':
        return jsonify(result)

    img_arr_old = face_utils.read_image_from_url(url_old)
    face_acc_old = FaceAccredit(img_arr_old)
    face_arr_old,face_in_old = face_acc_old.face_encoding()

    if(not face_in_old):
        result = {"result":"failed","msg":"no face in url_old"}
        return jsonify(result)

    img_arr_new = face_utils.read_image_from_url(url_new)
    face_acc_new = FaceAccredit(img_arr_new)
    face_arr_new,face_in_new = face_acc_new.face_encoding()

    if(not face_in_new):
        result = {"result":"failed","msg":"no face in url_new"}
        return jsonify(result)

    dis_result = face_acc_old.face_compare(face_arr_new)
    result = {"result":"success","msg":"compare success","prob":str(1 - dis_result[0])}
    return jsonify(result)

@app.route('/face/binding',methods=['POST'])
def face_binding():
    '''
    1. 传入参数: 身份证号码,身份证照片url/或用户最新证件照
    2. 处理流程: 判断照片中是否有人脸,如果有: 生成 `NP_身份证号码.npy`文件
    3. 返回参数: 如果有头像,返回绑定成功;否则返回绑定失败;
    '''
    idcard_id = ''
    face_img_url = ''
    result = {"code":"400","msg":"参数缺少或错误"}
    request_data = request.get_json()
    if 'idcard_id' in request_data:
        idcard_id = request_data['idcard_id']
    if 'face_img_url' in request_data:
        face_img_url = request_data['face_img_url']
    if idcard_id is '' or face_img_url is '':
        return jsonify(result)

    img_arr = face_utils.read_image_from_url(face_img_url)
    face_acc = FaceAccredit(img_arr)
    face_arr_list,face_in_img = face_acc.face_encoding()

    if len(face_arr_list) == 1 and face_in_img:
        face_utils.save_arr_to_file(face_arr_list[0],idcard_id)
        result = {"code":"0","msg":"绑定成功"}
    else:
        result = {"code":"500","msg":"绑定失败"}
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001)

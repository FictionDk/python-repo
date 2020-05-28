# -*- coding: utf-8 -*-
from flask import Flask,jsonify,request
import face_utils
from core import FaceAccredit
import json

app = Flask(__name__)

@app.route('/face/compare',methods=['POST'])
def face_compare():
    """比对两张图片是否有人脸和相似度
    Args:
        url_old: 身份证旧照
        url_new: 实时拍摄新照
    Return: 
        比对相似度,json
    """
    request_data = request.get_json()
    url_old, url_new = '',''
    result = {"code": "400", "status":"failed","msg":"参数缺少或错误"}
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
        result = {"code": "400", "result":"failed","msg":"no face in url_old"}
        return jsonify(result)

    img_arr_new = face_utils.read_image_from_url(url_new)
    face_acc_new = FaceAccredit(img_arr_new)
    face_arr_new,face_in_new = face_acc_new.face_encoding()

    if(not face_in_new):
        result = {"code": "400", "result":"failed","msg":"no face in url_new"}
        return jsonify(result)

    dis_result = face_acc_old.face_compare(face_arr_new)
    result = {"code": "0", "result":"success","msg":"compare success","prob":str(1 - dis_result[0])}
    return jsonify(result)

@app.route('/face/binding',methods=['POST'])
def face_binding():
    '''Give an image url and idcardid, build the 128-dimension face encoding npy file for face in the image
    :param idcard_id 身份证号码
    :param face_img_url 单人照片
    :return sucess or failed
    '''
    idcard_id, face_img_url = '',''
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

@app.route('/face/identify',methods=['POST'])
def face_identification():
    '''根据已绑定的`128-dimension face encoding npy file`查询已存在的人脸信息
    :param face_img_url 人脸照片
    :return 相似度大于指定阈值的身份证编码 eg: [{"idcard_id":"450225198208107439","prob": 0.5867}]
    '''
    face_img_url = ''
    result = {"code":"400","msg":"参数缺少或错误"}
    request_data = request.get_json()
    if 'face_img_url' in request_data:
        face_img_url = request_data['face_img_url']
    if face_img_url is '':
        return jsonify(result)

    img_arr = face_utils.read_image_from_url(face_img_url)
    face_acc = FaceAccredit(img_arr)
    face_arr_list,face_in_img = face_acc.face_encoding()
    if face_in_img: 
        face_npy_list, face_name_list = face_utils.get_npy_list()
        dis_results = face_acc.face_compare(face_npy_list)
        if dis_results.ndim == 1:
            identifactions = face_utils.identifaction_result_build(dis_results.tolist(), face_name_list, 0.55)
            result = {"code": "0", "msg": "identify success", "data": identifactions}
        else:
            result = {"code":"500","msg":"identify failed, result ndim is " + str(dis_results.ndim)}
    else:
        result = {"code":"400","msg":"no face in face_img_url"}
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001)

# -*- coding: utf-8 -*-
import face_recognition

class FaceAccredit():
    # img_arr: 传入的原始图片数组(Must be 8bit gray or RGB image)
    def __init__(self,img_arr=None):
        self._face_in_img = False  # 传入图片是否含有人脸
        self._face_arr_list = None  # 传入头像的人脸解析结果
        self._face_locations = None  # 传入头像的人脸位置
        self.set_face_img_arr(img_arr)

    # 设置原始图片数组
    def set_face_img_arr(self,img_arr):
        if img_arr is not None:
            self._img_arr = img_arr

    # 图片人脸特征抽取
    def face_encoding(self,img_arr=None):
        if img_arr is None:
            img_arr = self._img_arr
        face_in_img = False
        face_arr_list = face_recognition.face_encodings(img_arr)
        if len(face_arr_list) == 0:
            print("hog模式抽取图片人脸特征失败,启用cnn算法抽取")
            face_locations = self._face_location(img_arr)
            face_arr_list = face_recognition.face_encodings(img_arr,face_locations)
            if len(face_arr_list) > 0:
                face_in_img = True
        else:
            face_in_img = True
        self._face_arr_list = face_arr_list
        return face_arr_list,face_in_img

    # 获取人脸定位
    def _face_location(self,image_arr=None):
        face_locations = face_recognition.face_locations(self._img_arr)
        if(len(face_locations) == 0):
            print("hog模式定位图片人脸失败,启用cnn算法")
            face_locations = face_recognition.face_locations(self._img_arr,number_of_times_to_upsample=1,model="cnn")
        return face_locations

    # 人脸相似度比对
    def face_compare(self,face_arr_list):
        dis_results = face_recognition.face_distance(face_arr_list,self._face_arr_list[0])
        return dis_results

    # 人脸图片切割
    def _img_cutting_by_location(self,image,face_location):
        top,right,bottom,left = face_location
        return image[top:bottom,left:right]

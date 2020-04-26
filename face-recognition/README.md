# face_compare

> 使用face_recognition包以及Flask搭建的一个人脸对比的restful服务端框架

1. 使用docker部署安装(使用base_dockerfile/Dockerfile预装环境,确保不用每次更新都要重新打包环境镜像)

2. 可以直接导入/出`stpass/base_face`镜像,避免因为网络问题出现构建失败
 - `docker load < xxx.tar`
 - `docker tag <img_id> stpass/base_face:latest`(如果镜像名为none)
 - `sh deploy.sh`

## 环境使用

```
docker cp assert face_compare:/root/
docker cp demo.py face_compare:/root/
docker cp face_test.py face_compare:/root/
docker cp face_utils.py face_compare:/root/

docker cp face_compare:/root/assert/ .
```

## 版本(1.1)

### 接口设计

#### 身份绑定

1. 传入参数: 身份证号码,身份证照片url/或用户最新证件照
2. 处理流程: 判断照片中是否有人脸,如果有: 生成 `NP_身份证号码.npy`文件
3. 返回参数: 如果有头像,返回绑定成功;否则返回绑定失败;

#### 人脸识别

1. 传入参数: 待识别照片Url
2. 处理流程: 识别照片是否有人脸,如果有: 在已存在人脸库中检索是否有已存在
3. 返回参数: 如果存在,返回身份证号码;否则返回识别失败

#### 人脸比对

1. 传入参数: 待识别照片Url_1,待识别照片Url_2
2. 处理流程: 识别照片中是否有人脸,如果有: 比对两个人脸的相似度
3. 返回参数: 如果都存在人脸,返回相似度;否则返回比对失败

#### 身份认证

1. 传入参数: 身份证号码,身份证正面照片url,视频抓拍照片list
2. 处理流程: 判断照片中是否有人脸,如果有,比对身份证和抓拍照片;
3. 返回参数: 如果比对均大于0.6,返回成功码(身份证号对称加密);否组返回认证失败

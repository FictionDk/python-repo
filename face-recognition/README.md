# face_compare
  
> 使用face_recognition包以及Flask搭建的一个人脸对比的restful服务端框架

1. 使用docker部署安装(使用base_dockerfile/Dockerfile预装环境,确保不用每次更新都要重新打包环境镜像)

2. 可以直接导入/出`stpass/base_face`镜像,避免因为网络问题出现构建失败
 - `docker load < xxx.tar`
 - `docker tag <img_id> stpass/base_face:latest`(如果镜像名为none)
 - `sh deploy.sh`

3. docker cp face_compare.py  stpass/face_compare:/face_compare.py
# Zanthpara

zanthoxylum and paramiko

## ftp_file
```
from ftplib import FTP

ftp = FTP()
ftp.set_debuglevel(2)
ftp.connect('192.168.20.250',8021)
ftp.login('www','wwwadmin021')
```

## xftp_utils

> 基于paramiko实现的ssh2连接,包括xftp+ssh2

### Teleport模块

#### 功能描述
1. 下拉源远程服务的文件到本地
2. 将存储本地的文件上传到目标远程服务
3. 执行目标远程服务的命令

#### 服务打包
`pyinstaller -F -i ./assert/e.ico -n Zanth xftp_utils.py ../file-opt/file_utils.py`


### pycryptodome 模块

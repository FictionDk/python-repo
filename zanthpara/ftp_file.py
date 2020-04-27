# -*- coding: utf-8 -*-
from ftplib import FTP

def get_user():
    user = 'www'
    pwd = 'wwwadmin021'
    return user,pwd

def get_address():
    ip = '192.168.20.250'
    port = 8021
    return ip,port

def get_file_name():
    file_name = 'E:\\home\\python\\python-repo\\ftp_demo\\README.md'
    return file_name

def process():
    ip,port = get_address()
    user,pwd = get_user()
    with FTP() as ftp:
        ftp.connect(ip,port,timeout=3600)
        ftp.login(user,pwd)
        print(ftp.nlst())
        remote_path = '/var/www/html/wechat-reim/README.md'
        fb = open(get_file_name(),'rb')
        ftp.storbinary('STOR ' + remote_path,fb)
        ftp.quit()

if __name__ == '__main__':
    process()

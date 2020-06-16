# -*- coding: utf-8 -*-
import os
import paramiko
import time
import sys
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from base64 import b64encode
from base64 import b64decode

WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILE_UTIL_DIR = os.path.join(WORK_DIR,"file-opt")
sys.path.append(FILE_UTIL_DIR)
import file_utils

class ZanthAES(object):

    def _add_to_16(self, content):
        '''对密钥/偏移量进行长度填充
        Args:
            content 带填充值
        Returns: 返回符合规定长度的值(16,24,32 bytes)
        '''
        content = bytes(content, encoding='utf8')
        while len(content) % 16 != 0:
            content += b'\0'
        return content

    def ecb_encrypt(self, text, key):
        '''对内容加密
        Args:
            text 需要加密的原文
            key 处理密钥
        Returns: 返回加密后的内容
        '''
        key = self._add_to_16(key)
        text = text.encode('utf-8')
        cipher = AES.new(key, AES.MODE_ECB)
        data = cipher.encrypt(pad(text, AES.block_size))
        return b64encode(data).decode('utf-8')

    def ecb_decrypt(self, text, key):
        '''对内容解密
        Args:
            text 字符串 需要解密的已加密内容
            key 字符串 解密需要的密钥
        Returns: 字符串 返回加密后的内容,解密失败返回None
        '''
        try:
            key = self._add_to_16(key)
            text = b64decode(text.encode('utf-8'))
            cipher = AES.new(key, AES.MODE_ECB)
            pt = unpad(cipher.decrypt(text), AES.block_size)
            return pt.decode()
        except(ValueError, KeyError, Exception) as e:
            print("Incorrect decryption for text: %s from  key: %s; Error= %s" % (text,key,str(e)))
            return

class CannotReadFile(RuntimeError):
    pass

class ConnConfig(object):

    def __init__(self):
        '''初始化
        Args:
            _source_conf 源目标连接配置
            _target_conf
            _key 配置密钥
            _aes 解密对象
        '''
        source_conf_path = file_utils.get_full_filename('config','source_conf.jl')
        target_conf_path = file_utils.get_full_filename('config','target_conf.jl')
        self._source_conf = self._get_conf_from_file(source_conf_path)
        self._target_conf = self._get_conf_from_file(target_conf_path)
        self._key = 'Zanthoxylum'
        self._aes = ZanthAES()

    def get_source_conf(self):
        '''读取源服务连接配置
        Returns: user, passwd, ip, port
        '''
        source_list = list(self._source_conf.values())
        return source_list[0], self._aes.ecb_decrypt(source_list[1], self._key), \
            self._aes.ecb_decrypt(source_list[2], self._key), source_list[3]

    def get_target_conf(self):
        '''读取目标服务连接配置
        Returns: user, passwd, ip, port
        '''
        target_list = list(self._target_conf.values())
        return target_list[0], self._aes.ecb_decrypt(target_list[1], self._key), \
            self._aes.ecb_decrypt(target_list[2], self._key), target_list[3]

    def get_source_pwd(self):
        '''读取源服务文件路径
        Returns: /path/to/
        '''
        return self._source_conf['pwd']

    def get_target_pwd(self):
        '''读取目标服务文件路径
        Returns: /path/to/
        '''
        return self._target_conf['pwd']

    def _get_conf_from_file(self,filepath):
        '''读取指定路径的配置文件内容,返回table
        Args:
            filepath: 文件全路径字符串,如`/root/pwd/config.jl`
        Returns:
            返回文件的全路径
        Raises:
            ConfigIsNone: 无法从配置文件读取内容
        '''
        conf_str = None
        conf_json = {}
        with open(filepath,'r',encoding="utf-8") as f:
            conf_str = f.readline()
            if len(conf_str) > 0:
                conf_json = json.loads(conf_str)
        if(conf_json == {}):
            raise CannotReadFile('[%s] must fill with content like \
            {"user": "xx", "passwd": "xx", "ip":"192.168.3.1", "port": 22, "pwd": "/path/to/"}' % filepath)
        return conf_json

class Teleport():

    def __init__(self):
        self.config = ConnConfig()
        source_pwd = self.config.get_source_pwd()
        target_pwd = self.config.get_target_pwd()
        prefix = self.__get_prefix()
        suffix = self.__get_suffix()
        self.file_name = prefix + time.strftime("%Y%m%d", time.localtime()) + suffix
        self.source = source_pwd + self.file_name
        self.local = file_utils.get_full_filename('assert',self.file_name)
        self.target = target_pwd + self.file_name
        self.target_trans = None

    def __get_prefix(self):
        return 'berry_sup_summary_'

    def __get_suffix(self):
        return '.sql.tar.gz'

    def __get_exec(self):
        target_pwd = self.config.get_target_pwd()
        return 'cd %s &&  sh mysql_sync_static.sh' % target_pwd

    def __get_sftp(self, user, passwd, ip, port):
        trans = paramiko.Transport((ip,int(port)))
        trans.connect(username=user,password=passwd)
        sftp = paramiko.SFTPClient.from_transport(trans)
        return trans,sftp

    def download(self):
        '''使用xftp协议下载服务中指定路径下的文件到本地
        '''
        user, passwd, ip, port = self.config.get_source_conf()
        print("%s / %s -> %s Starting..." % (ip,self.source, self.local))
        trans,sftp = self.__get_sftp(user, passwd, ip, port)
        sftp.get(self.source,self.local)
        sftp.close()
        trans.close()
        print("%s -> %s End..." % (self.source, self.local))

    def upload(self):
        '''使用xftp协议上传本地文件到指定远程服务器
        '''
        user, passwd, ip, port = self.config.get_target_conf()
        print("%s -> [%s] %s Starting..." % (self.local, ip, self.target))
        trans,sftp = self.__get_sftp(user, passwd, ip, port)
        sftp.put(self.local, self.target)
        self.target_trans = trans
        sftp.close()
        print("%s -> %s End..." % (self.local, self.target))

    def exec(self):
        '''使用ssh协议执行远程服务器上的命令
        '''
        exec_command = self.__get_exec()
        print("exec %s Starting..." % exec_command)
        ssh = paramiko.SSHClient()
        if self.target_trans is None:
            self.upload()
        ssh._transport = self.target_trans
        stdin, stdout, stderr = ssh.exec_command(exec_command)
        print(stdout.read().decode(),"|",stderr.read().decode())
        self.target_trans.close()

def main():
    try:
        teleport = Teleport()
        teleport.download()
        teleport.exec()
        pass
    except Exception as e:
        print(e)

def conf_test():
    conn_conf = ConnConfig()
    print(conn_conf.get_source_conf())
    print(conn_conf.get_target_conf())
    print(conn_conf.get_source_pwd())
    print(conn_conf.get_target_pwd())

def aes_test():
    key = 'Zanthoxylum'
    text = 'paramiko'
    aes = ZanthAES()
    encrypt_data = aes.ecb_encrypt(text, key)
    print(encrypt_data)
    print(aes.ecb_decrypt(encrypt_data, key))
    print(aes.ecb_decrypt("P2wQjONezpgsHlS3fH82tA==", key))


if __name__ == '__main__':
    main()
    time.sleep(10)
    # aes_test()
    # conf_test()

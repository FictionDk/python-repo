# -*- coding: utf-8 -*-

import psycopg2
import os
import json
import sys
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class CannotReadFile(RuntimeError):
    pass

class ConnConfig(object):
    def __init__(self):
        '''初始化
        Args:
            _source_conf 目标连接配置
        '''
        conn_conf_path = self.get_current_path('config','postgres_conf.jl')
        self._conn_conf = self._get_conf_from_file(conn_conf_path)

    def get_current_path(self,directory,filename=None):
        '''获取当前执行目录下的指定路径下的文件名
        Args:
            directory: 目录名称
            filename: 文件名,可为空
        Returns:
            返回文件或文件的全路径
        Raises:
            ArgsNotNull: 参数不能为空
        '''
        if directory is None:
            dir_name = BASE_DIR
        else:
            dir_name = os.path.join(BASE_DIR,directory)
            if not os.path.exists(dir_name): # 确保目录存在
                os.makedirs(dir_name)
        if filename is None:
            return dir_name
        full_name = os.path.join(dir_name,filename)
        if not os.path.isfile(full_name): # 确保文件存在
            with open(full_name,'a+',encoding="utf-8") as f:
                f.close()
        return full_name

    def get_conn_conf(self):
        '''读取源服务连接配置
        Returns: user, passwd, ip, port, db
        '''
        cnf_list = list(self._conn_conf.values())
        return cnf_list[0], cnf_list[1], cnf_list[2], cnf_list[3], cnf_list[4]

    def _get_conf_from_file(self, filepath):
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
            {"user": "xx", "passwd": "xx", "ip":"192.168.3.1", "port": 15433, "db": "healthcare"}' % filepath)
        return conf_json

class Postgres():
    def __init__(self,host,port,username,password,db):
        '''初始化连接
        '''
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._db = db
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=db
        )

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class LabelUtils():
    def __init__(self):
        cnf = ConnConfig()
        username, password, host, port, db = cnf.get_conn_conf()
        self.__pg = Postgres(host, port, username, password, db)

    def get_random_labels(self, number):
        query_label_sql = 'select * from blood_label order by created_at desc limit {}'.format(number)
        cur = self.__pg.get_cursor()
        cur.execute(query_label_sql)
        rows = cur.fetchall()
        labels = []
        end_product_num = 0
        for row in enumerate(rows):
            label = self.__label_build(row)
            labels.append(label)
            if label.get('flag') == '55':
                end_product_num += 1
        self.__pg.commit()
        return labels, end_product_num

    def __label_build(self, row):
        label = {}
        if len(row) != 2:
            return label
        if len(row[1]) != 10:
            return label
        label['tid'] = row[1][0]
        label['sid'] = row[1][1]
        label['flag'] = row[1][2]
        label['product'] = row[1][3]
        if isinstance(row[1][8], datetime.datetime):
            label['time'] = row[1][8].strftime("%Y-%m-%d %H:%M:%S")
        else:
            label['time'] =row[1][8]
        return label

def test():
    util = LabelUtils()
    labels, num = util.get_random_labels(2000)
    print(num)

test()
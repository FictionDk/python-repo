# -*- coding: utf-8 -*-

import psycopg2
import os
import json
import sys

WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILE_UTIL_DIR = os.path.join(WORK_DIR,"file-opt")
sys.path.append(FILE_UTIL_DIR)
import file_utils

class CannotReadFile(RuntimeError):
    pass

class ConnConfig(object):
    def __init__(self):
        '''初始化
        Args:
            _source_conf 目标连接配置
        '''
        conn_conf_path = file_utils.get_full_filename('config','postgres_conf.jl')
        self._conn_conf = self._get_conf_from_file(conn_conf_path)

    def get_conn_conf(self):
        '''读取源服务连接配置
        Returns: user, passwd, ip, port, db
        '''
        cnf_list = list(self._conn_conf.values())
        return cnf_list[0], cnf_list[1], cnf_list[2], cnf_list[3], cnf_list[4]

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


def clean_data():
    user_conf_count = {}
    cnf = ConnConfig()
    username, password, host, port, db = cnf.get_conn_conf()
    pg = Postgres(host, port, username, password, db)
    query_monitor_user_confs_sql = 'select * from monitor_user_conf order by id desc'
    delete_over_date = 'delete from monitor_user_conf where id = '
    cur = pg.get_cursor()
    cur.execute(query_monitor_user_confs_sql)
    rows = cur.fetchall()
    row_show(rows[1])
    for row in enumerate(rows):
        content_tuple = row[1]
        cid = int(content_tuple[0])
        key = str(content_tuple[1]) + str(content_tuple[2])
        value = user_conf_count.get(key)
        if value is None:
            value = ',0'
        [lid, count] = value.split(',')
        if int(count) > 0:
            print("%d is over" % (cid))
            cur.execute(delete_over_date + str(cid))

        user_conf_count[key] = str(cid) + "," + str(int(count) + 1)

    pg.commit()
    pg.close()
    print(user_conf_count)

def row_show(row):
    for col in enumerate(row):
        print("%s, %s" % (type(col[1]), col[1]))


clean_data()
# -*- coding: utf-8 -*-

import pymysql
import os
import json
from xlsx import Xlsx

class MySql():
    def __init__(self,host,port,username,password,db):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._db = db
        self.conn = pymysql.Connect(
            host=host,
            port=port,
            user=username,
            passwd=password,
            db=db,
            charset="utf8"
        )

    def _get_cursor(self):
        return self.conn.cursor()

class Conf():
    def __init__(self,conf_name):
        path = self._get_conf_file_path(conf_name)
        conf = self._get_conf_from_file(path)
        self.host = conf["host"]
        self.port = conf["port"]
        self.username = conf["username"]
        self.password = conf["password"]

    # 获取配置文件路径,返回文件路径
    def _get_conf_file_path(self,conf_name):
        dir_name = os.path.join(os.getcwd(),'conf')
        file_full_name = os.path.join(dir_name,conf_name + '.conf')
        if not os.path.exists(dir_name):
            raise Exception(file_full_name,"..Not exists")
        return file_full_name

    # 读取指定路径的配置文件内容,返回table
    def _get_conf_from_file(self,filepath):
        conf_str = None
        conf_json = {}
        with open(filepath,'r',encoding="utf-8") as f:
            conf_str = f.readline()
            if len(conf_str) > 0:
                conf_json = json.loads(conf_str)
        return conf_json

# 将用户数据更新到certified_donator(phone_nubmer,idcard_id)
def _update_certified_donator(mysql_client,donators):
    sql = "UPDATE certified_donator SET phone_number = '%s' WHERE idcard_id = '%s' "
    cursor = mysql_client._get_cursor()
    for donator in donators:
        cursor.execute(sql % donator)
    mysql_client.conn.commit()

# 将用户数据存入xlsx
def _save_donators_to_xsls(donators,filename):
    xlsx = Xlsx(filename + '.xlsx')
    xlsx.write_to_xlsx(donators)

# 数据库中获取身份证号,手机号,姓名
def _get_donators_from_db(mysql_client):
    sql = "select phone_number,idcard_id from supervise_donator where phone_number is not NULl;"
    cursor = mysql_client._get_cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows

def main():
    sup_conf = Conf('sup_donator')
    db_client = MySql(sup_conf.host,sup_conf.port,sup_conf.username,sup_conf.password,'berry_sup')
    donators = _get_donators_from_db(db_client)
    _save_donators_to_xsls(donators,'sup_donator')
    db_client = MySql(sup_conf.host,sup_conf.port,sup_conf.username,sup_conf.password,'berry_sup_statistics')
    _update_certified_donator(db_client,donators)

def test():
    sup_conf = Conf('sup_donator')
    db_client = MySql(sup_conf.host,sup_conf.port,sup_conf.username,sup_conf.password,'berry_sup')
    donators = _get_donators_from_db(db_client)
    print(type(donators))
    for d in donators:
        print(d)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
# Analysis of Error log of dept

import json
import os
import openpyxl as op

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

# 打包后的环境
if getattr(sys, 'frozen', False):
    BASE_DIR = BUNDLE_DIR

class FileUtils():
    '''文件工具
    '''
    def read_dict_list_from_json(self,file_path=None):
        dict_list = []
        with open(file_path,'r+',encoding="utf-8") as f:
            dict_list_str = f.read()
            if len(dict_list_str) > 0:
                dict_list = json.loads(dict_list_str)
        return dict_list

    def read_line_list_from_txt(self,file_path=None):
        line_list = []
        for line in open(file_path,'r',encoding="utf-8"):
            if len(line) > 0:
                line_list.append(line)
        return line_list

class AnalysisUtil():
    '''数据分析工具
    '''
    # eg: rows [{ "deptNo": xxx, "type": xxx, "count": xxx}]
    # eg: type_mapping ["NEW,新浆员注册",...]
    # eg: out{ "田阳光明": { "采浆": 3 , "体检": 5}}
    def count_err_dict_by_status(self, rows, type_mapping, status=400):
        type_dict = {}
        for type_name_str in type_mapping:
            type_arr = type_name_str.split(',')
            type_dict[type_arr[0]] = type_arr[1].replace('\n','')
        err_dict = {}
        for row in rows:
            dept_name = row['deptName']
            dept_counter = err_dict.get(dept_name)
            if dept_counter == None:
                dept_counter = {}

            type_name = type_dict[row['type']]
            dept_counter[type_name] = row['count']
            err_dict[dept_name] = dept_counter
        return err_dict

class XlsxUtil():
    # eg: rows { "田阳光明": { "采浆": 3 , "体检": 5}}
    # eg: type_mapping ["NEW,新浆员注册",...]
    def dict2xlsx(self, rows, type_mapping, path):
        header = ['']
        header_map = {}
        for i,type_name_str in enumerate(type_mapping):
            type_name = type_name_str.split(',')[1].replace('\n','')
            header.append(type_name)
            header_map[type_name] = i
        wb = op.Workbook()
        ws = wb['Sheet']
        ws.append(header)
        print(rows)
        for name,type_dict in rows.items():
            row_line = [name,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            for t_name,count in type_dict.items():
                index = header_map.get(t_name)
                row_line[index+1] = count
            ws.append(row_line)
        wb.save(path)

def test():
    err_list_path = os.path.join(BASE_DIR,'docs','err.json')
    type_mapping_path = os.path.join(BASE_DIR,'docs','type.mapping')
    err_result_path = os.path.join(BASE_DIR,'docs', 'err_result.xlsx')
    fu = FileUtils()
    err_list = fu.read_dict_list_from_json(err_list_path)
    type_mapping = fu.read_line_list_from_txt(type_mapping_path)

    au = AnalysisUtil()
    err_dict = au.count_err_dict_by_status(err_list, type_mapping)

    xu = XlsxUtil()
    xu.dict2xlsx(err_dict, type_mapping, err_result_path)


if __name__ == '__main__':
    test()

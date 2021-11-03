# -*- coding: utf-8 -*-
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前目录路径
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))  # 父级目录
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))  # 打包后的程序执行目录
if getattr(sys, 'frozen', False):  # 打包后的环境
    BASE_DIR = BUNDLE_DIR

def match_for_line(line):
    try:
        start = line.find('{')
        end = line.find('}')
        line = line[start:end + 1]
        r = {}
        if line == '':
            return r
        kv_list = line.split('=')
        if len(kv_list) < 7:
            return r
        k1 = kv_list[0].replace(' ','').replace('{','')
        v1 = kv_list[1].split(',')[0].replace(' ','')
        k2 = kv_list[1].split(',')[1].replace(' ','')
        v2 = kv_list[2].split(',')[0].replace(' ','')
        k3 = kv_list[2].split(',')[1].replace(' ','')
        v3 = kv_list[3].split(',')[0].replace(' ','')
        k4 = kv_list[3].split(',')[1].replace(' ','')
        v4 = ','.join(kv_list[4].split(',')[0:-1])
        k5 = kv_list[4].split(',')[-1].replace(' ','')
        v5 = kv_list[5].split(',')[0].replace(' ','')
        k6 = kv_list[5].split(',')[1].replace(' ','')
        v6 = kv_list[6].replace(' ','').replace('}','')
        r[k1] = v1
        r[k2] = v2
        r[k3] = v3
        r[k4] = v4
        r[k5] = v5
        r[k6] = v6
        pass
    except Exception as e:
        print(str(e) + "|" + str(line))
    return r

def read_from_file(fullname):
    content = []
    for line in open(fullname,'r',encoding="utf-8"):
        if line.find('ERROR') != -1:
            dic = match_for_line(line)
            if dic != {}:
                content.append(match_for_line(line))
    return content

def write_to_file(content):
    for line in content:
        if line['status'] != '429':
            with open('1028.jl','a',encoding='utf-8') as f:
                f.write(str(line) + "\n")

def get_data():
    content = []
    filenames = os.listdir(BASE_DIR)
    for filename in filenames:
        if filename.find('.log') != -1:
            content += read_from_file(os.path.join(BASE_DIR,filename))
    return content

def main():
    content = get_data()
    write_to_file(content)

def test():
    line = 'xxx{timestamp=2021-10-28 18:22:43, status=400, error=Bad Request, message=参数格式不正确或缺失,详情:特免血浆缺少免疫类型[vaccinationType],可选:[HEPATITIS_B|RABIES|TETANUS|ANTHRAX], path=/api/plasmacollect/save, deptNo=4509220353}'
    line = 'xxx{timestamp=2021-10-28 17:53:03, status=500, error=Internal Server Error, message=系统错误,详情: String index out of range: 27,请将错误详情一并发送系统管理员, path=/api/log/add}'
    content = match_for_line(line)
    print(content)
    # print(json.dumps(content, ensure_ascii=False, indent="\t"))

if __name__ == '__main__':
    main()

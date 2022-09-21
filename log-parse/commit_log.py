# -*- coding: utf-8 -*-
from cgitb import reset
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前目录路径

# git log --pretty=format:"%an|%s|%ai|%f" --since="30 day ago" > commit.log
# git log --shortstat --since="30 day ago" > commit1.log
# git log --stat|perl -ne 'END { print $c } $c += $1 if /(\d+) insertions/'
# --author user
def read_from_file(fullname):
    content, count = [], 0
    for line in open(fullname,'r',encoding="utf-8"):
        count += 1
        if line.find('Merge remote-tracking branch') == -1:
            arr = line.strip().split('|')
            result = {}
            result['name'] = arr[0]
            result['msg'] = arr[1]
            result['date'] = str(arr[2])[0:10]
            content.append(result)
    print(0, count)
    return content

def run():
    content = read_from_file(os.path.join(BASE_DIR,'commit.log'))
    result = {}
    print(1,len(content))
    print(content[10])
    for line in content:
        count = 0 if line['name'] not in result else result[line['name']]
        count += 1
        result[line['name']] = count
    print(result)

run()
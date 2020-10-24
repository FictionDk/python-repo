# Random

## 描述

创建随机人物,包括地址,身份证号,姓名  

文件 | 描述
--- | ---
souce.spider.py | 原始资源爬取
souce.district.json | 远程爬取的全国地区编码和地区名称
core.py | 创建随机数据
api.py | 基于flask提供api接口访问


## requirements
`pipreqs . --encoding=utf-8 --force`
当前目录强制生成/覆盖`requirements.txt`

> 注: 使用前需要确保已经安装`pipreqs`,`pip install pipreqs`


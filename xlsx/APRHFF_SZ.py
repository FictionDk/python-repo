# -*- coding: utf-8 -*-
# Analysis of Public Rental Housing Formula Form

import os
import sys
import openpyxl
import json
from pyecharts.charts import Bar
from pyecharts.charts import Pie
from pyecharts import options as opts
from pyecharts.charts import Map
# from pyecharts.render import make_snapshot
# from snapshot_selenium import snapshot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
BUNDLE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

class ArgsNotNull(RuntimeError):
    pass

# 打包后的环境
if getattr(sys, 'frozen', False):
    BASE_DIR = BUNDLE_DIR

def get_title():
    return 'Analysis of Public Rental Housing Formula Form'

class FileUtils():
    '''文件工具
    '''

    def get_full_filename(self,directory,filename=None):
        '''获取当前执行目录下的指定路径下的文件名
        Args:
            filename: 文件名,可为空,返回文件夹全路径
            directory: 目录名称
        Returns:
            返回文件的全路径
        Raises:
            ArgsNotNull: 参数不能为空
        '''
        if directory is None:
            raise ArgsNotNull("directory can not be None")
        dir_name = os.path.join(BASE_DIR,directory)

        # 确保目录存在
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        if filename is None:
            return dir_name
        full_name = os.path.join(dir_name,filename)
        # 确保文件存在
        if not os.path.isfile(full_name):
            with open(full_name,'a+',encoding="utf-8") as f:
                f.close()
        return full_name

    def get_filename_in_dir(self,directory):
        '''获取当前执行目录下的指定路径下的文件名列表
        Args:
            directory: 目录名称

        Returns:
            返回文件的全路径
        '''
        dir_full_path = self.get_full_filename(directory)
        return os.listdir(dir_full_path)

class AnalysisUtil():
    '''数据分析工具
    '''

    def __init__(self):
        self.provinces = {}
        self.province_json = self._provinces()
        self.p_shows = []

    def area_analysis(self, idcard):
        province_code = idcard[0:2]
        if not province_code.isdigit():
            province_code = '00'
        count = self.provinces.get(province_code, 0)
        count += 1
        self.provinces[province_code] = count

    def area_result_show(self):
        if len(self.p_shows) > 1:
            return self.p_shows
        for (k,v) in self.provinces.items():
            p_name = self.province_json.get(k, '其他')
            self.p_shows.append((p_name, v))
        return self.p_shows

    def _provinces(self):
        fu = FileUtils()
        path = fu.get_full_filename('docs', 'province.json')
        provinces_json = {}
        with open(path,'r+',encoding="utf-8") as f:
            provinces_str = f.read()
            if len(provinces_str) > 0:
                provinces_json = json.loads(provinces_str)
        return provinces_json

class ChartUtil():
    '''可视化工具
    '''

    def bar(self, datasets):
        print(datasets)
        datasets = sorted(datasets, key=lambda d: d[1], reverse=True)
        count = list(map(lambda d: d[1], datasets))
        provinces = list(map(lambda d: d[0], datasets))
        print(provinces)
        Bar().add_xaxis(provinces).add_yaxis('', count).set_global_opts(
            title_opts=opts.TitleOpts(title=get_title()),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
        ).render("docs/bar.html")

    def pie(self, datesets):
        pie = Pie(init_opts=opts.InitOpts(width='500px',height='500px',page_title=get_title()))
        pie.add("", datesets).render("docs/pies.html")

    def map(self, datasets):
        print(datasets)
        m = Map(init_opts=opts.InitOpts(width="1100px", height="700px"))
        m.add("count", datasets, maptype="china")
        m.set_global_opts(
            title_opts=opts.TitleOpts(title=get_title()),
            visualmap_opts=opts.VisualMapOpts(
                max_=3000,
                min_=100,
                range_text=['High', 'Low'],
                is_calculable=True,
                range_color=["lightskyblue", "yellow", "orangered"]),
            legend_opts=opts.LegendOpts(is_show=False),).render('docs/map.html')

def _print_row(i,row):
    for j,col in enumerate(row):
        print("row[%d] col[%d] = %s" % (i, j,str(col.value)))

def _formate_data(i, row, au):
    row_contain_data = lambda row: len(row) >= 7 and str(row[0].value).isdigit() or row[0].value is None
    if row_contain_data(row):
        au.area_analysis(row[4].value)

def main():
    fu = FileUtils()
    au = AnalysisUtil()
    cu = ChartUtil()

    path = fu.get_full_filename('docs', '8181977.xlsx')

    workbook = openpyxl.load_workbook(path,read_only=True)
    workspace = workbook.active
    rows = workspace.rows
    for i,row in enumerate(rows):
        _formate_data(i, row, au)
    cu = ChartUtil()
    cu.map(au.area_result_show())
    cu.pie(au.area_result_show())
    cu.bar(au.area_result_show())

def test():
    datasets = [('广东', 10003), ('河北', 177), ('江苏', 136), ('山西', 152), ('安徽', 411), ('湖南', 2780)]
    get_k = lambda d: d[0]
    test = list(map(get_k, datasets))
    print(test)
    print("gogog")
    print(sorted(datasets, key=lambda d: d[1]), reversed=True)

if __name__ == '__main__':
    main()

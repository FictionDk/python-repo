# -*- coding: utf-8 -*-

import openpyxl
import os

class Xlsx():
    def __init__(self,filename):
        self._full_path = self._get_full_filename('doc',filename)

    def _get_full_filename(self,dir,filename):
        dir_name = os.path.join(os.getcwd(),dir)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        full_name = os.path.join(dir_name,filename)
        if not os.path.isfile(full_name):
            with open(full_name,'a+',encoding="utf-8") as f:
                f.close()
        return full_name

    def write_to_xlsx(self,rows):
        workbook = openpyxl.Workbook()
        ws = workbook.active
        for row in rows:
            ws.append(row)
        workbook.save(self._full_path)

    def read_from_xlsx(self):
        workbook = openpyxl.load_workbook(self._full_path,read_only=True)
        ws = workbook.active
        return ws.rows


def test():
    rows = [('row1,column1','row1,column2'),
            ('row2,column1','row2,column2')]

    xlsx = Xlsx('test.xlsx')
    xlsx.write_to_xlsx(rows)
    xlsx = Xlsx('sup_donator.xlsx')
    donators = xlsx.read_from_xlsx()
    for index,row in enumerate(donators):
        if index % 500 == 0:
            print(index,":",row[0].value,'->',row[1].value)

test()

# Common Excel Python Utils

## openpyxl

> doc: https://openpyxl.readthedocs.io/en/latest/

### openpyxl sample demo
```python
#创建一个工作薄对象,也就是创建一个excel文档
wb = Workbook()

#指定当前显示（活动）的sheet对象
ws = wb.active

ws.append([1, 2, 3])
wb.save("sample.xlsx")

wb = load_workbook('1.xlsx')
# 根据sheet名称选取
ws = wb['sheet']

for row in ws.rows:
    for cell in row:
        print(cell.value)
```

### python.str is,==

```python
s1 = "hello"
s2 = "hellotest"
s1 is s2[0:5] # False
s1 == s2[0:5] # True
```

### python.shutil

```python
try:
    shutil.move(row[0].value,row[1].value)
except FileNotFoundError as e:
    print("FileNotFoundError")
```

### 服务打包
`pyinstaller -F -i ./docs/e64.ico -n AELD AELD.py`

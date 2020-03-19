# -*- coding: utf-8 -*-
import sys
import turtle

# 列表
def list_test():
    a = [1,2,3,4,5,6,7]
    b = ["张三","李四","王五"]
    c = [1,3,4,"4","5",b]
    print(a)
    print(b)
    # 列表名[起:止] -- 前闭后开区间
    print(c[0:2])
    # 列表名[起:止:步长] -- 步长有方向
    print(a[4:1:-2])
    print(a[6::-2])
    # 从倒数第二个开始
    print(a[-2::-2])

# 元组,一旦定义不能改变
def tuple_test():
    f = (1,2,3)
    print(f[1])

# 字典
def dict_test():
    dic = {1:"123","name":"张三","height":180}
    print(dic[1])
    print(dic["name"])
    dic["age"] = 18
    print(dic["age"])

def if_test():
    age = input("请输入你的年龄 \n")
    if int(age) > 18:
        print("你成年了!")
    else:
        print("你还未成年!")

def for_test():
    h = ["a","b","c","d"]
    for i in h:
        print(i)
        for j in h:
            print(j)

def while_test():
    x,y = 1,2
    while True:
        x = x + 1
        y = y + 1
        print(x,",",y)
        if x > 5 or y > 5:
            break
    pass

def turtle_test():
    t = turtle.Pen()
    t.forward(100)
    t.left(90)
    t.forward(100)
    t.left(90)

def turtle_for_test():
    t = turtle.Pen()
    for i in range(0,4):
        t.forward(100)
        t.left(90)

def main():
    print(sys.stdout.encoding)
    # list_test()
    # tuple_test()
    # dict_test()
    # if_test()
    # for_test()
    # while_test()
    # turtle_test()
    turtle_for_test()
    pass

if __name__ == "__main__":
    main()

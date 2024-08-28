# -*- coding: utf-8 -*-
import sys

#x = (1+2+3+4+...+n)*(1+2+3+4+...+n)
# 定义一个函数，方法名叫add,参数为n,类型为int
def add(n:int):
    # 初始化一个局部变量，初始值为0，生效范围在当前函数内
    r = 0
    # 循环，从1到n
    for i in range(1,n+1):
        print(f"{r}+{i}",end="=")
        # 赋值 r 当前值加1
        r = r + i
        print(i)
    # 返回r的平方
    return r*r


if __name__ == '__main__':
    n = sys.argv[1]
    print(n)
    print(add(int(n)))
    print(sum(range(1, int(n)+1))**2)


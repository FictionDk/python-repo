import tensorflow as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

'''
预备知识:
    tf.where函数
    tf.greate函数
    np.random函数
    np.vstack函数
    np.mgrid[]
    np.ravel
    np.c_[]
'''

a = tf.constant([1,2,3,1,1])
b = tf.constant([0,1,3,4,5])
c = tf.where(tf.greater(a,b),a,b)  # greate判断a > b, True返回a,False返回b
print("c: \n",c,";\n",type(c))  # tf.Tensor([1 2 3 4 5], shape=(5,), dtype=int32)

rdm = np.random.RandomState(seed=1)  # 使用常量seed保证每次随机数相同
a = rdm.rand()  # 返回一个随机标量
b = rdm.rand(2,3)   # 返回2行3列的随机矩阵
print("a: \n",a)
print("b: \n",b)

a = np.array([1,2,3])
b = np.array([4,5,6])
c = np.vstack((a,b))  # 将两个数组按垂直方向叠加
print("c: \n",c)

x,y = np.mgrid[1:3:1, 2:4:0.5]  # mgrid[起始值:结束值:步长, 起始值:结束值:步长, ...]
x_ravel = x.ravel()  # x.ravel() 将x变成1维数组
grid = np.c_[x.ravel(),y.ravel()]
print("x: \n",x)
print("y: \n",y)
print("x_ravel: \n",x_ravel)
print("grid: \n",grid)

# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def data_type_test():
    a = tf.constant([1.0,2.0])
    b = tf.constant([3.0,4.0])
    print(a + b)

def data_oper_test():
    # 定义两阶张量
    x = tf.constant([[1.0,2.0]])
    w = tf.constant([[3.0],[4.0]])
    # x*w,计算图
    y = tf.matmul(x,w)
    return y

def data_sess_test():
    y = data_oper_test()
    print(y)
    with tf.Session() as sess:
        print(sess.run(y))

def data_variable():
    # random.normal() 生成正态分布随机数
    # 2行3列
    # 标准差为2
    # 均值为0
    # 随机种子为1
    w = tf.Variable(tf.random.normal([2,3],stddev=2,mean=0,seed=1))
    print("type(w) is ",type(w))
    print(w)

def data_example():
    # 占位
    x = tf.placeholder(tf.float32,shape=(None,2))
    # 输入和参数
    w1 = tf.Variable(tf.random.normal([2,3],stddev=1,seed=1))
    w2 = tf.Variable(tf.random.normal([3,1],stddev=1,seed=1))
    # 定义前向传播过程
    a = tf.matmul(x,w1)
    y = tf.matmul(a,w2)

    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        print(sess.run(y,feed_dict={x:[[0.7,0.5],
            [0.2,0.3],[0.3,0.4],[0.4,0.5]
        ]}))

def main():
    # data_type_test()
    # data_oper_test()
    # data_sess_test()
    # data_variable()
    data_example()

if __name__ == "__main__":
    main()

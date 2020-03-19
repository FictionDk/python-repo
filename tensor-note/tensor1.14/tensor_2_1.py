# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 张量
def data_type_test():
    a = tf.constant([1.0,2.0])
    b = tf.constant([3.0,4.0])
    print(a + b)

# 图定义
def data_oper_test():
    # 定义两阶张量
    x = tf.constant([[1.0,2.0]])
    w = tf.constant([[3.0],[4.0]])
    # x*w,计算图
    y = tf.matmul(x,w)
    return y

# 会话
def data_sess_test():
    y = data_oper_test()
    print(y)
    print(type(y))
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

def data_full_example():
    BATCH_SIZE = 8
    seed = 23455
    # 基于种子产生随机数
    rng = np.random.RandomState(seed)
    # 随机返回32行2列的矩阵
    X = rng.rand(32,2)
    # 从X中取出1行,判断如果和小于1,给Y赋值1(正确答案)
    # 如果和不小于1,给Y赋值0
    Y = [[int(x0 + x1 < 1)] for (x0,x1) in X]
    print(X)
    print(Y)
    # 定义神经网络输入,参数,和输出;定义前向传播过程
    x = tf.placeholder(tf.float32,shape=(None,2))
    y_ = tf.placeholder(tf.float32,shape=(None,1))

    w1 = tf.Variable(tf.random.normal([2,3],stddev=1,seed=1))
    w2 = tf.Variable(tf.random.normal([3,1],stddev=1,seed=1))

    a = tf.matmul(x,w1)
    y = tf.matmul(a,w2)
    # 定义损失函数及反向传播方法
    loss = tf.reduce_mean(tf.square(y - y_))
    train_step = tf.train.GradientDescentOptimizer(0.001).minimize(loss)

    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        # 未训练的参数值
        print(sess.run(w1))
        print(sess.run(w2))

        # 训练模型
        STEPS = 30000
        for i in range(STEPS):
            start = (i * BATCH_SIZE) % 32
            end = start + BATCH_SIZE
            sess.run(train_step,feed_dict={x:X[start:end],y_:Y[start:end]})
            if i % 500 == 0:
                tatol_loss = sess.run(loss,feed_dict={x:X,y_:Y})
                print("%d traing loss on all date is %g" % (i,tatol_loss))
        print(sess.run(w1))
        print(sess.run(w2))

def main():
    # data_type_test()
    # data_oper_test()
    data_sess_test()
    # data_variable()
    # data_example()
    # data_full_example()


if __name__ == "__main__":
    main()

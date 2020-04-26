# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

BATCH_SIZE = 8
SEED = 23544
COST = 1
PROFIT = 9

# 损失函数
# 模拟生成参数数据
def rand_data():
    rdm = np.random.RandomState(SEED)
    X = rdm.rand(32,2)
    # x1,x2是影响日销量的因素,y_(已知答案,最佳情况: 产量=销量)
    Y_ = [[x1 + x2 + (rdm.rand() / 10 - 0.05)] for (x1,x2) in X]
    # 拟造数据集X,Y_: y = x1 + x2 噪声: ~.0.05 拟合可以预测销量的函数
    return X,Y_

# 预测酸奶日销量,酸奶成本(COST)1元,利润(PROFIT)9元
# 自定义损失函数:
# 预测的y少了,损失利润; 预测的y多了,损失成本; reduce_sum: 损失求和
# loss = tf.; reduce_sum(tf.where(tf.greater(y,y_),COST(y-y_),PROFIT(y_-y)))
def main():
    X,Y_ = rand_data()
    # 1.定义神经网络的输入,参数和输出,定义前向传播过程
    x = tf.placeholder(tf.float32, shape=(None,2))
    y_ = tf.placeholder(tf.float32, shape=(None,1))
    w1 = tf.Variable(tf.random.normal([2,1],stddev=1,seed=1))
    y = tf.matmul(x,w1)
    # 2.定义损失函数及反向传播方法
    # loss_mse = tf.reduce_mean(tf.square(y_ - y))
    loss = tf.reduce_sum(tf.where(tf.greater(y,y_),(y - y_) * COST, (y_ - y) * PROFIT))
    train_step = tf.train.GradientDescentOptimizer(0.001).minimize(loss)

    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        STEPS = 20000
        for i in range(STEPS):
            start = (i * BATCH_SIZE) % 32
            end = start + BATCH_SIZE
            sess.run(train_step, feed_dict={x: X[start:end], y_:Y_[start:end]})
            if i % 500 == 0:
                print("after %d training steps , w1 is " % i)
                print(sess.run(w1))
        print(sess.run(w1))

if __name__ == "__main__":
    main()

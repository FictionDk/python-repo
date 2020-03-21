# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

'''
激活函数

- 非线性: 激活函数非线性,多层神经网络可逼近所有函数
- 可微: 优化器大多数用梯度下降更新参数
- 单调: 保证单层网络的损失函数是凸函数
- 近似恒等: 当参数初始化为随机小值时,网络更稳定

激活函数输出值的范围:
- 输出为有限时,基于梯度的优化方法更稳定
- 输出为无限时,建议调小学习率

Sigmoid函数
Tanh函数
Relu函数
Leaky Relu函数

损失函数

NN优化目标: loss最小
均方误差mse: tf.reduce_mean(tf.square(y_-y))
交叉熵ce(表征两个概率之间的距离):
    - tf.nn.softmax(y)  tf.losses.categorical_crossentropy(y_,y)
    - tf.nn.softmax_cross_entropy_with_logits(y_,y)
'''

SEED = 23445
epoch = 20000
lr = 0.001

def build_rand_data():
    '''
    模拟生成参数数据
    拟造数据集X,Y_: y = x1 + 2*x2 噪声: ~.0.05
    '''
    rdm = np.random.RandomState(SEED)  # 生成[0,1)之间的随机数
    X = rdm.rand(64,2)
    # x1,x2是影响日销量的因素,y_(已知答案,最佳情况: 产量=销量)
    Y_ = [[x1 + 2 * x2 + (rdm.rand() / 10 - 0.05)] for (x1,x2) in X]
    return X,Y_

X,Y_ = build_rand_data()
X = tf.cast(X,dtype=tf.float32)
w1 = tf.Variable(tf.random.normal([2,1],stddev=1,seed=1))

CUSTOMIZE_LOSS = True
COST = 1  # 成本
PROFILE = 9  # 利润

print("Start w1 is : \n",w1.numpy())

# 拟合最优的w1
for epoch in range(epoch):
    with tf.GradientTape() as tape:
        y = tf.matmul(X,w1)  # 求前向转播结果
        if CUSTOMIZE_LOSS:
            # 自定义损失函数,当预测的y(产量)大于Y_时,损失成本,y小于Y_时,损失利润
            loss = tf.reduce_sum(tf.where(tf.greater(y,Y_),(y - Y_) * COST,(Y_ - y) * PROFILE))
        else:
            loss = tf.reduce_mean(tf.square(Y_ - y))  # 损失函数(均方误差)
    grads = tape.gradient(loss,w1)  # 求偏导
    w1.assign_sub(lr * grads)  # 更新w1

    if epoch % 3000 == 0:
        print("After %s epoch, loss is %f" % (epoch,loss))
        print("w1 is :\n",w1.numpy())

print("Final w1 is : \n",w1.numpy())

# 计算两组参数与指定概览之间的距离
loss_ce1 = tf.losses.categorical_crossentropy([1,0,1],[0.6,0.2,0.2])
loss_ce2 = tf.losses.categorical_crossentropy([1,0,1],[0.6,0.1,0.3])
loss_ce3 = tf.losses.categorical_crossentropy([1,0,1],[0.9,0.1,0.6])

print("loss_ce1= %f,loss_ce2= %f,loss_ce3 = %f" % (loss_ce1,loss_ce2,loss_ce3))

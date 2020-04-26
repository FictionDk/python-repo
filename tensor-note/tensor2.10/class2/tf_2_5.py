# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

'''
欠拟合 && 过拟合
- 欠拟合: 模型对训练数据学习的不够
- 过拟合: 模型对训练数据过于依赖,对新数据缺少预测,泛化性弱

正则化:
    - 一般对参数w加权,弱化训练集数据噪声
    - 可有效缓解过拟合
    - L1正则化,大概率使得很多参数变为0,通过稀疏参数,减少复杂度
    - L2正则化,使得很多参数接近0,通过减小参数值降低复杂度

'''
COUNT = 1024 + 512

def build_y(x1,x2):
    '''
    模拟y_的结果,y_ = 25 < x1*x1 + x2*x2 ? 1 : 0 噪声: ~.0.5
    '''
    noise_value = np.random.uniform(-0.5,0.5)
    if x1 * x1 + x2 * x2 + noise_value < 25:
        return 1
    else:
        return 0

def build_rand_data():
    '''
    模拟生成参数数据
    '''
    x = np.random.uniform(-9, 9,((COUNT, 2)))  # 生成 row 行 2 列 [0,10)之间的随机数矩阵
    y_ = [[build_y(x1, x2)] for (x1, x2) in x]
    return x, y_

def backward_train(x_train, y_, use_regularization=False):
    '''
    反向传播训练模型,返回模型参数
    '''
    x = tf.cast(x_train, tf.float32)
    y_ = tf.cast(y_, tf.float32)

    train_db = tf.data.Dataset.from_tensor_slices((x, y_)).batch(32)

    w1 = tf.Variable(tf.random.normal([2, 11]), dtype=tf.float32)
    b1 = tf.Variable(tf.constant(0.01, shape=[11]))

    w2 = tf.Variable(tf.random.normal([11, 1]), dtype=tf.float32)
    b2 = tf.Variable(tf.constant(0.01, shape=[1]))

    lr = 0.005
    epoch = 800

    for epoch in range(epoch):
        for step, (x, y_) in enumerate(train_db):
            with tf.GradientTape() as tape:
                h1 = tf.matmul(x, w1) + b1
                h1 = tf.nn.relu(h1)
                y = tf.matmul(h1,w2) + b2
                loss = tf.reduce_mean(tf.square(y_ - y))

                if use_regularization:  # 是否使用正则化
                    loss_regularization = []
                    loss_regularization.append(tf.nn.l2_loss(w1))  # L2正则化
                    loss_regularization.append(tf.nn.l2_loss(w2))
                    loss_regularization = tf.reduce_sum(loss_regularization)  # tf.reduce_sum(...) 矩阵求和
                    loss = loss + 0.03 * loss_regularization

            variables = [w1, b1, w2, b2]
            grads = tape.gradient(loss, variables)

            w1.assign_sub(lr * grads[0])
            b1.assign_sub(lr * grads[1])
            w2.assign_sub(lr * grads[2])
            b2.assign_sub(lr * grads[3])

        if epoch % 100 == 0:
            print("epoch: %d, loss = %f" % (epoch,float(loss)))

    return w1, b1, w2, b2

def plt_predict_data_prepare(w1, b1, w2, b2, color):
    '''
    plt准备预测数据线数据
    '''
    xx, yy = np.mgrid[-10:10:.1, -10:10:.1]

    grid = np.c_[xx.ravel(), yy.ravel()]
    grid = tf.cast(grid, tf.float32)

    probs = []

    for x_test in grid:
        h1 = tf.matmul([x_test], w1) + b1
        h1 = tf.nn.relu(h1)
        y = tf.matmul(h1, w2) + b2
        probs.append(y)

    probs = np.array(probs).reshape(xx.shape)
    plt.contour(xx, yy, probs, levels=[.5], colors=color)  # 等高线绘制

def plt_raw_data_prepare(x_train, y_c):
    '''
    plt准备原始数据点数据
    '''
    x1 = x_train[:, 0]
    x2 = x_train[:, 1]
    plt.scatter(x1, x2, color=np.squeeze(y_c))

x_train, y_ = build_rand_data()
y_c = [['red' if y[0] else 'blue'] for y in y_]

w1, b1, w2, b2 = backward_train(x_train, y_)  # 不使用正则化计算模型
plt_predict_data_prepare(w1, b1, w2, b2, 'green')  # 将预测结果加入plt待展示(绿线)
w1, b1, w2, b2 = backward_train(x_train, y_, True)  # 使用正则化计算模型
plt_predict_data_prepare(w1, b1, w2, b2, 'yellow')  # 将预测结果加入plt展示(黄线)

plt_raw_data_prepare(x_train, y_c)
plt.show()

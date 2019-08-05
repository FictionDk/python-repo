# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import tensorflow as tenf
import numpy as np
import matplotlib.pyplot as plt
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

BATCH_SIZE = 30
SEED = 2

# 损失函数(正则化)  处理模型过拟合情况

def get_base_data():
    rdm = np.random.RandomState(SEED)
    X = rdm.randn(300,2)
    Y_ = [int(x0 * x0 + x1 * x1 < 2) for (x0,x1) in X]
    Y_c = [['red' if y else 'blue'] for y in Y_]
    X = np.vstack(X).reshape(-1,2)
    Y_ = np.vstack(Y_).reshape(-1,1)
    # print(X)
    # print(Y_)
    # print(Y_c)
    plt.scatter(X[:,0],X[:,1], c=np.squeeze(Y_c))
    plt.show()
    return X,Y_,Y_c

# 定义神经网络的输入,参数和输出;定义前向传播过程
def get_weight(shape, regularizer):
    w = tf.Variable(tf.random.normal(shape),dtype=tf.float32)
    tf.add_to_collection('losses',tenf.contrib.layers.l2_regularizer(regularizer)(w))
    return w

def get_biass(shape):
    b = tf.Variable(tf.constant(0.01,shape=shape))
    return b

def main():
    X,Y_,Y_c = get_base_data()
    x = tf.placeholder(tf.float32,shape=(None,2))
    y_ = tf.placeholder(tf.float32,shape=(None,1))
    # 隐藏层
    w1 = get_weight([2,11],0.01)
    b1 = get_biass([11])
    y1 = tf.nn.relu(tf.matmul(x,w1) + b1)
    # 输出层
    w2 = get_weight([11,1],0.01)
    b2 = get_biass([1])
    y = tf.matmul(y1,w2) + b2

    loss_mse = tf.reduce_mean(tf.square(y - y_))
    loss_total = loss_mse + tf.add_n(tf.get_collection('losses'))

    train_step = tf.train.AdamOptimizer(0.0001).minimize(loss_mse)
    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        STEPS = 40000
        for i in range(STEPS):
            start = (i * BATCH_SIZE) % 300
            end = start + BATCH_SIZE
            sess.run(train_step,feed_dict={x:X[start:end],y_:Y_[start:end]})
            if i % 200 == 0:
                loss_mse_v = sess.run(loss_mse,feed_dict={x:X,y_:Y_})
                print("After %d steps, loss is: %f" % (i,loss_mse_v))
        xx,yy = np.mgrid[-3:3:.01,-3:3:.01]
        grid = np.c_[xx.ravel(),yy.ravel()]
        probs = sess.run(y,feed_dict={x:grid})
        probs = probs.reshape(xx.shape)
        print("w1 :",sess.run(w1))
        print("b1 :",sess.run(b1))
        print("w2 :",sess.run(w2))
        print("b2 :",sess.run(b2))
    plt.scatter(X[:,0],X[:,1],c=np.squeeze(Y_c))
    plt.contour(xx,yy,probs,levels=[.5])
    plt.show()

if __name__ == "__main__":
    main()

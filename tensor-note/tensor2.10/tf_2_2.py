# -*- coding: utf-8 -*-

import tensorflow as tf
import time
'''
神经网络复杂度
    - 空间复杂度(层数=参与计算的层(隐藏层+输出层);总参数=总w(=层数*节点数)+总b)
    - 时间复杂度(乘加运算数)

指数衰减学习率=初始学习率*学习率衰减率(当前轮数/多少轮衰减一次)
'''

LEARNING_RATE_BASE = 0.2  # 初始学习率
LEARNING_RATE_DECAY = 0.99  # 学习率衰减率
LEARNING_RATE_STEP = 1  # 多少轮更新一次学习率, 一般: 总样本数/BATCH_SIZE

epoch = 40

w = tf.Variable(tf.constant(5,dtype=tf.float32))
for epoch in range(epoch):
    lr = LEARNING_RATE_BASE * LEARNING_RATE_DECAY ** (epoch / LEARNING_RATE_STEP)
    with tf.GradientTape() as tape:
        loss = tf.square(w + 1)
    grads = tape.gradient(loss,w)

    w.assign_sub(lr * grads)
    print("After %s epoch,w is %f, loss is %f,lr is %f" % (epoch,w.numpy(),loss,lr))
    time.sleep(0.1)

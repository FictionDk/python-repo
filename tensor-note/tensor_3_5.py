# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 指数衰减学习率: 学习率随着训练轮数变化而动态更新
# 设损失函数 loss=(w+1)^2,令w初值为5,反向传播求解最优解;

LEARNING_RATE_BASE = 0.1  # 初始学习率
LEARNING_RATE_DECAY = 0.99  # 学习率衰减率
LEARNING_RATE_STEP = 1  # 多少轮更新一次学习率, 一般: 总样本数/BATCH_SIZE

def main():
    global_step = tf.Variable(0,trainable=False)
    learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE,global_step,
        LEARNING_RATE_STEP,LEARNING_RATE_DECAY,staircase=True)
    w = tf.Variable(tf.constant(5,dtype=tf.float32))
    loss = tf.square(w + 1)
    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss,global_step=global_step)
    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        for i in range(40):
            sess.run(train_step)
            learning_rate_val = sess.run(learning_rate)
            global_step_val = sess.run(global_step)
            w_val = sess.run(w)
            loss_val = sess.run(loss)
            print("After %s steps: g_s is %f, w is %f, l_r is %f,loss is %s"
% (i,global_step_val,w_val,learning_rate_val,loss_val))

if __name__ == "__main__":
    main()

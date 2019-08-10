# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
from tensorflow.examples.tutorials.mnist import input_data
# from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
import tensor_4_1_mnist_forward as mnist_forward
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

BATCH_SIZE = 200
LEARNING_RATE_BASE = 0.1
LEARNING_RATE_DECAY = 0.99
REGULARIZER = 0.001
STEPS = 50000
MOVING_AVERAGE_DECAY = 0.99
MODEL_SAVE_PATH = "./model/"
MODEL_NAME = "mnist_model"

def backword(mnist):
    # 给训练数据x,标签y_占位
    x = tf.placeholder(tf.float32,[None,mnist_forward.INPUT_NODE])
    y_ = tf.placeholder(tf.float32,[None,mnist_forward.OUTPUT_NODE])
    # 使用前向传播过程,设置是否正则化,计算预测结果y
    y = mnist_forward.forward(x, REGULARIZER)
    # 轮数计数器,不可训练
    global_step = tf.Variable(0,trainable=False)

    # 设置损失函数
    ce = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y,labels=tf.argmax(y_,1))
    cem = tf.reduce_mean(ce)
    loss = cem + tf.add_n(tf.get_collection('losses'))

    # 设定指数衰减学习率
    learning_rate = tf.train.exponential_decay(
        LEARNING_RATE_BASE,
        global_step,
        mnist.train.num_examples / BATCH_SIZE,
        LEARNING_RATE_DECAY,
        staircase=True)

    # 定义反向传播方法
    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss,global_step=global_step)

    # 滑动平均: 记录一段时间内模型的所有参数w和b各自的平均值,影子值,追随参数的变化而变化
    # MOVING_AVERAGE_DECAY: 滑动平均衰减率
    ema = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY,global_step)
    ema_op = ema.apply(tf.trainable_variables())
    with tf.control_dependencies([train_step,ema_op]):
        train_op = tf.no_op(name='train')

    saver = tf.train.Saver()

    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)

        for i in range(STEPS):
            xs,ys = mnist.train.next_batch(BATCH_SIZE)
            _,loss_value,step = sess.run([train_op,loss,global_step],feed_dict={x: xs,y_:ys})
            if i % 1000 == 0:
                print("After %d training steps,loss on training batch is %g." % (step,loss_value))
                saver.save(sess,os.path.join(MODEL_SAVE_PATH,MODEL_NAME),global_step=global_step)

def main():
    mnist = input_data.read_data_sets("./data/",one_hot=True)
    backword(mnist)

if __name__ == "__main__":
    main()

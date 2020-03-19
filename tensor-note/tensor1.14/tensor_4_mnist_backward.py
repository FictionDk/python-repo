# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
from tensorflow.examples.tutorials.mnist import input_data
# from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
import tensor_4_mnist_forward as mnist_forward
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 一个训练batch中的训练数据个数。
# 个数越小越接近随机梯度下降；数字越大时，训练越接近梯度下降
BATCH_SIZE = 200
# 基础的学习率
LEARNING_RATE_BASE = 0.1
# 学习率的衰减率
LEARNING_RATE_DECAY = 0.99
# 描述模型复杂度的正则化项在损失函数中的系数
REGULARIZER = 0.0001
# 训练轮数
STEPS = 50000
# 滑动平均衰减率
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

    # 定义交叉熵损失
    # 因为交叉熵一般和softmax回归一起使用，
    # 所以 tf.nn.sparse_softmax_cross_entropy_with_logits函数
    # 对这两个功能进行了封装。
    # 这里使用该函数进行加速交叉熵的计算，
    # 第一个参数是不包括softmax层的前向传播结果。
    # 第二个参数是训练数据的正确答案，
    # 这里得到的是正确答案的这里使用该函数进行加速交叉熵的计算，
    # 第一个参数是不包括softmax层的前向传播结果。
    # 第二个参数是训练数据的正确答案，这里得到的是正确答案的正确编号
    ce = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y,labels=tf.argmax(y_,1))
    # 计算当前batch中所有样例的交叉熵平均值
    cem = tf.reduce_mean(ce)
    # 总损失等于交叉熵损失和正则化损失的和
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
    # 在训练神经网络时,每过一遍数据既需要通过反向传播来更新神经神经网络的参数，
    # 又需要更新每一个参数的滑动平均值,这里的 tf.control_dependencies
    with tf.control_dependencies([train_step,ema_op]):
        train_op = tf.no_op(name='train')

    saver = tf.train.Saver()

    with tf.Session() as sess:
        # 初始化
        tf.global_variables_initializer().run()

        ckpt = tf.train.get_checkpoint_state(MODEL_SAVE_PATH)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess,ckpt.model_checkpoint_path)

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

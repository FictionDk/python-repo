# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import tensorflow as tensor
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
'''
使用Lenet,卷积优化cifar-10模型训练
'''

# 图片分辨率
IMAGE_SIZE = 32
NUM_CHANNELS = 3
# 第一层行列分辨率
CONV1_SIZE = 5
# 第一层卷积核个数
CONV1_KERNEL_NUM = 32
# 第二层行列分辨率
CONV2_SIZE = 5
# 第二层卷积核个数
CONV2_KERNEL_NUM = 64
# 第三层行列分辨率
CONV3_SIZE = 5
# 第三层卷积核个数
CONV3_KERNEL_NUM = 128
FC_SIZE = 512
# 输出层节点个数(分类个数)
OUTPUT_NODE = 10

def get_weight(shape, regularizer):
    w = tf.Variable(tf.truncated_normal(shape,stddev=0.1))
    if regularizer is not None:
        tf.add_to_collection('losses',tensor.contrib.layers.
            l2_regularizer(regularizer)(w))
    return w

def get_bias(shape,bias=0.0):
    # 准确率太低,将偏置从原有的全0改为0.1
    initial = tf.constant(bias, shape=shape)
    b = tf.Variable(initial)
    return b

def conv2d(x,w):
    # 参数描述:
    # 输入描述x[batch,行分辨率,列分辨率,通道数],
    # 卷积核描述w[行分辨率,列分辨率,通道数,卷积核个数],
    # 核滑动步长strides[1,行步长,列步长,1],
    # 填充模式padding
    return tf.nn.conv2d(x,w,strides=[1,1,1,1],padding="SAME")

def max_pool_2x2(x):
    # 输入描述[batch,行分辨率,列分辨率,通道数],
    # 池化核描述[1,行分辨率,列分辨率,1],
    # 池化核滑动步长[1,行步长,列步长,1],
    # 填充模式
    return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')

def forward(x,train,regularizer):
    conv1_w = get_weight([CONV1_SIZE,CONV1_SIZE,NUM_CHANNELS,CONV1_KERNEL_NUM],regularizer)
    conv1_b = get_bias([CONV1_KERNEL_NUM])
    conv1 = conv2d(x,conv1_w)
    relu1 = tf.nn.relu(tf.nn.bias_add(conv1,conv1_b))
    pool1 = max_pool_2x2(relu1)

    conv2_w = get_weight([CONV2_SIZE,CONV2_SIZE,CONV1_KERNEL_NUM,CONV2_KERNEL_NUM],regularizer)
    conv2_b = get_bias([CONV2_KERNEL_NUM],0.01)
    conv2 = conv2d(pool1,conv2_w)
    relu2 = tf.nn.relu(tf.nn.bias_add(conv2,conv2_b))
    pool2 = max_pool_2x2(relu2)

    conv3_w = get_weight([CONV3_SIZE,CONV3_SIZE,CONV2_KERNEL_NUM,CONV3_KERNEL_NUM],regularizer)
    conv3_b = get_bias([CONV3_KERNEL_NUM],0.1)
    conv3 = conv2d(pool2,conv3_w)
    relu3 = tf.nn.relu(tf.nn.bias_add(conv3,conv3_b))
    pool3 = max_pool_2x2(relu3)

    pool_shape = pool3.get_shape().as_list()
    nodes = pool_shape[1] * pool_shape[2] * pool_shape[3]
    reshaped = tf.reshape(pool3,[pool_shape[0],nodes])

    fcl_w = get_weight([nodes,FC_SIZE],regularizer)
    fcl_b = get_bias([FC_SIZE])
    fcl = tf.nn.relu(tf.matmul(reshaped,fcl_w) + fcl_b)
    if train:
        fcl = tf.nn.dropout(fcl,rate=0.5)

    fc2_w = get_weight([FC_SIZE,OUTPUT_NODE],regularizer)
    fc2_b = get_bias([OUTPUT_NODE])
    y = tf.matmul(fcl,fc2_w) + fc2_b
    return y

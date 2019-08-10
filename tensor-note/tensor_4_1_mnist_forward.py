# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import tensorflow as tensor
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
'''
前向传播过程定义
需要定义神经网络中的参数w和偏置b
'''
# 网络输入结点,(28*28图的像素个数)
INPUT_NODE = 784
# 输出节点,(0-9个分类)
OUTPUT_NODE = 10
# 隐藏层节点
LAYER1_NODE = 500

# 定义参数w
# shape: 参数w的形状
def get_weight(shape,regularizer):
    w = tf.Variable(tf.truncated_normal(shape,stddev=0.1))
    if regularizer is not None:
        tf.add_to_collection('losses',tensor.contrib.layers.l2_regularizer(regularizer)(w))
    return w

# 获取偏置b
# shape: 参数b的形状
def get_bias(shape):
    b = tf.Variable(tf.zeros(shape))
    return b

# 前向传播定义网络结构(预测模型)
# regularizer: 是否需要正则化(正则化权重)
def forward(x, regularizer):
    # 输入层到隐藏层,w1[784,500]
    w1 = get_weight([INPUT_NODE,LAYER1_NODE],regularizer)
    b1 = get_bias([LAYER1_NODE])
    # tf.nn.relu--激活函数,提高模型表达力
    # 实测结果,relu函数在本次手写数字识别中优于sigmoid函数
    y1 = tf.nn.relu(tf.matmul(x,w1) + b1)
    # y1 = tf.nn.sigmoid(tf.matmul(x,w1) + b1)
    # 隐藏层到输出层,w2[500,10]
    w2 = get_weight([LAYER1_NODE,OUTPUT_NODE],regularizer)
    b2 = get_bias([OUTPUT_NODE])
    y = tf.matmul(y1,w2) + b2
    return y

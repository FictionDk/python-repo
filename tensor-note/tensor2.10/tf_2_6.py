# -*- coding: utf-8 -*-

from sklearn import datasets
from matplotlib import pyplot as plt
import tensorflow as tf
import numpy as np
import time

'''
神经网络参数优化器

 - SGD, 常用梯度下降法
 - SGDM, 在SGD基础上增加一阶动量
 - Adagrad, 在SGD基础上增加二阶动量
 - RMSProp, 在SGD基础上增加二阶动量
 - Adam, 同时增加SGDM的一阶动量,和RMSPorp的二阶动量
'''
optimization_models = ['SGD','SGDM','Adagrad','RMSProp','Adam']

SEED = 116  # 随机种子方便与其他人测试结果对比
BATCH_SIZE = 32  # 每个批次组的数据个数

def data_prepare():
    x_data = datasets.load_iris().data  # 鸢尾花特征数据集
    y_data = datasets.load_iris().target  # 鸢尾花标签数据集

    np.random.seed(SEED)
    np.random.shuffle(x_data)
    np.random.seed(SEED)
    np.random.shuffle(y_data)
    tf.random.set_seed(SEED)

    x_train = x_data[:-30]  # 训练集
    y_train = y_data[:-30]
    x_test = x_data[-30:]  # 测试集,后30行
    y_test = y_data[-30:]

    x_train = tf.cast(x_train, tf.float32)
    x_test = tf.cast(x_test, tf.float32)

    return x_train, y_train,x_test,y_test

def optimization_process(optimization_model,epoch=500,global_step=0,loss_all=0):
    x_train, y_train,x_test,y_test = data_prepare()
    train_db = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(BATCH_SIZE)
    test_db = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(BATCH_SIZE)
    lr = 0.1  # 学习率
    # 生成神经网络的参数，4个输入特征故，输入层为4个输入节点；因为3分类，故输出层为3个神经元
    # 用tf.Variable()标记参数可训练
    # 使用seed使每次生成的随机数相同（方便教学，使大家结果都一致，在现实使用时不写seed）
    w1 = tf.Variable(tf.random.truncated_normal([4,3], stddev=0.1, seed=1))
    b1 = tf.Variable(tf.random.truncated_normal([3], stddev=0.1, seed=1))

    train_loss_results = []  # 每轮的loss记录列表
    test_acc = []  # 每轮的acc记录列表
    now_time = time.time()
    for epoch in range(epoch):  # 数据集级别的循环，每个epoch循环一次数据集
        for step, (x_train, y_train) in enumerate(train_db):  # batch级别的循环,每个step循环一个batch
            global_step += 1
            with tf.GradientTape() as tape:   # with结构记录梯度信息
                y = tf.matmul(x_train, w1) + b1   # 神经网络乘加运算
                y = tf.nn.softmax(y)  # 使输出y符合概率分布（此操作后与独热码同量级，可相减求loss）
                y_ = tf.one_hot(y_train, depth=3)  # 将标签值转换为独热码格式，方便计算loss和accuracy
                loss = tf.reduce_mean(tf.square(y_ - y))  # 采用均方误差损失函数mse
                loss_all += loss.numpy()  # 将每个step计算出的loss累加，为后续求loss平均值提供数据，这样计算的loss更准确
            grads = tape.gradient(loss, [w1, b1])  # 计算loss对各个参数的梯度

            if optimization_model is 'SGD':
                w1.assign_sub(lr * grads[0])  # 参数w1梯度自更新
                b1.assign_sub(lr * grads[1])  # 参数b梯度自更新
            elif optimization_model is 'SGDM':
                m_w, m_b = 0, 0
                beta = 0.9
                m_w = beta * m_w + (1 - beta) * grads[0]
                m_b = beta * m_b + (1 - beta) * grads[1]
                w1.assign_sub(lr * m_w)
                b1.assign_sub(lr * m_b)
            elif optimization_model is 'Adagrad':
                v_w, v_b = 0, 0
                v_w += tf.square(grads[0])
                v_b += tf.square(grads[1])
                w1.assign_sub(lr * grads[0] / tf.sqrt(v_w))
                b1.assign_sub(lr * grads[1] / tf.sqrt(v_b))
            elif optimization_model is 'RMSProp':
                v_w, v_b = 0, 0
                beta = 0.9
                v_w = beta * v_w + (1 - beta) * tf.square(grads[0])
                v_b = beta * v_b + (1 - beta) * tf.square(grads[1])
                w1.assign_sub(lr * grads[0] / tf.sqrt(v_w))
                b1.assign_sub(lr * grads[1] / tf.sqrt(v_b))
            elif optimization_model is 'Adam':
                m_w, m_b = 0, 0
                v_w, v_b = 0, 0
                beta1, beta2 = 0.9, 0.999
                # delta_w, delta_b = 0, 0
                m_w = beta1 * m_w + (1 - beta1) * grads[0]
                m_b = beta1 * m_b + (1 - beta1) * grads[1]
                v_w = beta2 * v_w + (1 - beta2) * tf.square(grads[0])
                v_b = beta2 * v_b + (1 - beta2) * tf.square(grads[1])
                m_w_correction = m_w / (1 - tf.pow(beta1, int(global_step)))
                m_b_correction = m_b / (1 - tf.pow(beta1, int(global_step)))
                v_w_correction = v_w / (1 - tf.pow(beta2, int(global_step)))
                v_b_correction = v_b / (1 - tf.pow(beta2, int(global_step)))
                w1.assign_sub(lr * m_w_correction / tf.sqrt(v_w_correction))
                b1.assign_sub(lr * m_b_correction / tf.sqrt(v_b_correction))
            else:
                raise Exception("Error optimization_model")

        train_loss_results.append(loss_all / 4)  # 将4个step的loss求平均记录在此变量中
        loss_all = 0

        # 测试部分
        total_correct, total_number = 0, 0  # total_correct预测对的样本个数
        for x_test, y_test in test_db:
            y = tf.matmul(x_test, w1) + b1
            y = tf.nn.softmax(y)
            pred = tf.argmax(y, axis=1)  # 返回y中最大值的索引，即预测的分类
            pred = tf.cast(pred, dtype=y_test.dtype)  # 将pred转换为y_test的数据类型
            # 若分类正确，则correct=1，否则为0，将bool型的结果转换为int型
            correct = tf.cast(tf.equal(pred, y_test), dtype=tf.int32)
            correct = tf.reduce_sum(correct)  # 将每个batch的correct数加起来
            total_correct += int(correct)  # 将所有batch中的correct数加起来
            # total_number为测试的总样本数，也就是x_test的行数，shape[0]返回变量的行数
            total_number += x_test.shape[0]
        acc = total_correct / total_number
        test_acc.append(acc)
    total_time = time.time() - now_time
    print("total_time: %d",total_time)
    return train_loss_results, test_acc, total_time

def plt_show(train_loss_results, test_acc, total_time, optimization_model):
    plt.title(optimization_model + ' Loss Function Curve')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.plot(train_loss_results, label="$Loss$")
    plt.legend()
    plt.show()

    plt.title(optimization_model + ' Acc Curve')
    plt.xlabel('Epoch ' + str(format(total_time, '.3f')))
    plt.ylabel('Acc')
    plt.plot(test_acc, label="$Accuracy$")
    plt.legend()
    plt.show()

for optimization_model in optimization_models:
    train_loss_results, test_acc, total_time = optimization_process(optimization_model)
    plt_show(train_loss_results, test_acc, total_time, optimization_model)

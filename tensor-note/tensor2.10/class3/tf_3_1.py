# -*- coding: utf-8 -*-

'''
使用keras搭建神经网络

model = tf.keras.models.Sequential([网络结构])  # 描述各层网络
网络结构举例:

1. 拉直层: tf.keras.layers.Flatten()  # 无计算,输入特征拉直
2. 全连接层: tf.keras.layers.Dense(神经元个数,activation="激活函数",
                            kernel_regularizer="正则化")
可选activation: relu, softmax, sigmoid, tanch, ...
可选kernel_regularizer: tf.keras.regularizers.l1(), tf.keras.regularizers.l2(), ...

3. 卷积层: tf.keras.layers.Conv2D(filters=卷积核个数, kernel_size=卷积核尺寸,
                            strides=卷积步长, padding="valid" or "")

4. LSTM(循环)层: tf.keras.layers.LSTM()

5. Compare: model.compile(optimizer=优化器, loss=损失函数, metrics=["准确率"])
Optimizer可选:
'sgd' or tf.keras.optimizers.SGD(lr=学习率,momentum=动量参数)
'adagrad' or tf.keras.optimizers.Adagrad(lr=学习率)
'adadelta' or tf.keras.optimizers.Adadelta(lr=学习率)
'adam' or tf.keras.optimizers.Adam(lr=学习率, beta_1=0.9, beta_2=0.999)
Loss可选:
'mes' or tf.keras.losses.MeanSquaredError()
'sparse_categorical_crossentropy' or tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
                from_logits=False输出前经过了概率分布/True输出前没有经过概率分布
Metrices可选:
'accuracy': y和y_都是数值, 如 y_=[1] y=[1]
'categorical_accuracy': y和y_都是独热码(概率分布), 如 y_=[0,1,0] y=[0.256,0.695,0.048]
'sparse_categorical_accuracy' y_是数值, y是独热码(概率分布) 如 y_=[1] y=[0.256,0.695,0.048]

6. Fit: model.fit(训练集输入特征, 训练集标签, batch_size=, epochs=,
                validation_data = (测试集的输入特征, 测试集的标签),
                validation_split = 从训练集划分多少比例给测试集,
                validation_freq = 多少次epoch测试一次)

7. Summary: model.summary()  打印训练网络
'''

import tensorflow as tf
from sklearn import datasets
import numpy as np

x_train = datasets.load_iris().data
y_train = datasets.load_iris().target

# 训练集乱序
np.random.seed(116)
np.random.shuffle(x_train)
np.random.seed(116)
np.random.shuffle(y_train)
tf.random.set_seed(116)

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(3, activation='softmax', kernel_regularizer=tf.keras.regularizers.l2())
])

model.compile(optimizer=tf.keras.optimizers.SGD(lr=0.1),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
    metrics=['sparse_categorical_accuracy'])

model.fit(x_train, y_train, batch_size=32, epochs=500, validation_split=0.2, validation_freq=20)

model.summary()

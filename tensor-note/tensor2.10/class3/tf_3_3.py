# -*- coding: utf-8 -*-

import tensorflow as tf

mnist = tf.keras.datasets.mnist

(x_train, y_train),(x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

# 搭建网络结构
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28,28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# 配置训练方法(优化器,损失函数,最终评价指标)
model.compile(optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['sparse_categorical_accuracy'])

# 执行训练过程
model.fit(x_train, y_train, epochs=10, validation_data=(x_test,y_test), validation_freq=2)

# 打印网络结构,统计参数数目
model.summary()

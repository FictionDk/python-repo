# -*- coding: utf-8 -*-
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPool2D, Dropout, Flatten, Dense
from tf_5_1_data_set import DataSets
import tf_5_0_utils as tf_utils

class Baseline(Model):
    def __init__(self):
        super(Baseline, self).__init__()
        # 卷积 层,Convolutional
        self.c1 = Conv2D(filters=6, kernel_size=(5,5), padding='same')
        # 批标准化, BN
        self.b1 = BatchNormalization()
        # 激活 层,Activation
        self.a1 = Activation('relu')
        # 池化 层,Pooling
        self.p1 = MaxPool2D(pool_size=(2,2), strides=2, padding='same')
        # dropout 层
        self.d1 = Dropout(0.2)

        self.flatten = Flatten()
        self.f1 = Dense(128, activation='relu')
        self.d2 = Dropout(0.2)
        self.f2 = Dense(10, activation='softmax')

    def call(self, x):
        # 卷积-- 特征提取器,CBAPD
        x = self.c1(x)
        x = self.b1(x)
        x = self.a1(x)
        x = self.p1(x)
        x = self.d1(x)

        x = self.flatten(x)
        x = self.f1(x)
        x = self.d2(x)
        y = self.f2(x)
        return y

dat = DataSets()
(x_train, y_train), (x_test, y_test) = dat.load_cifar10()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = Baseline()

history = tf_utils.model_train(model, "Baseline", x_train, y_train, x_test, y_test)

model.summary()

file = open('./weighs.txt', 'w')
for v in model.trainable_variables:
    file.write(str(v.name) + '\n')
    file.write(str(v.shape) + '\n')
    file.write(str(v.numpy()) + '\n')
file.close()

tf_utils.history_show(history)

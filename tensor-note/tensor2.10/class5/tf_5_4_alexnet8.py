# -*- coding: utf-8 -*-
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPool2D, Dropout, Flatten, Dense
from tf_5_1_data_set import DataSets
import tf_5_0_utils as tf_utils

class AlexNet8(Model):
    def __init__(self):
        super(AlexNet8, self).__init__()
        self.c1 = Conv2D(filters=96, kernel_size=(3,3))
        self.b1 = BatchNormalization()
        self.a1 = Activation('relu')
        self.p1 = MaxPool2D(pool_size=(3,3), strides=2)

        self.c2 = Conv2D(filters=256, kernel_size=(3,3))
        self.b2 = BatchNormalization()
        self.a2 = Activation('relu')
        self.p2 = MaxPool2D(pool_size=(3,3), strides=2)

        self.c3 = Conv2D(filters=384, kernel_size=(3,3), padding='same', activation='relu')
        self.c4 = Conv2D(filters=384, kernel_size=(3,3), padding='same', activation='relu')
        self.c5 = Conv2D(filters=256, kernel_size=(3,3), padding='same', activation='relu')
        self.p3 = MaxPool2D(pool_size=(3,3), strides=2)

        self.flatten = Flatten()
        self.f1 = Dense(2048, activation='relu')
        self.d1 = Dropout(0.5)
        self.f2 = Dense(2048, activation='relu')
        self.d2 = Dropout(0.5)
        self.f3 = Dense(10, activation='softmax')

    def call(self, x):
        x = self.c1(x)
        x = self.b1(x)
        x = self.a1(x)
        x = self.p1(x)

        x = self.c2(x)
        x = self.b2(x)
        x = self.a2(x)
        x = self.p2(x)

        x = self.c3(x)
        x = self.c4(x)
        x = self.c5(x)
        x = self.p3(x)

        x = self.flatten(x)
        x = self.f1(x)
        x = self.d1(x)
        x = self.f2(x)
        x = self.d2(x)
        y = self.f3(x)
        return y

dat = DataSets()
(x_train, y_train), (x_test, y_test) = dat.load_cifar10()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = AlexNet8()

history = tf_utils.model_train(model, "AlexNet8", x_train, y_train, x_test, y_test)

model.summary()

file = open('./weighs.txt', 'w')
for v in model.trainable_variables:
    file.write(str(v.name) + '\n')
    file.write(str(v.shape) + '\n')
    file.write(str(v.numpy()) + '\n')
file.close()

tf_utils.history_show(history)

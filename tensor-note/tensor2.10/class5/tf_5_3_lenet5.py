# -*- coding: utf-8 -*-

from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense
from tf_5_1_data_set import DataSets
import tf_5_0_utils as tf_utils


class LeNet5(Model):
    def __init__(self):
        super(LeNet5, self).__init__()
        self.c1 = Conv2D(filters=6, kernel_size=(5,5), activation='sigmoid')
        self.p1 = MaxPool2D(pool_size=(2,2), strides=2)
        self.c2 = Conv2D(filters=16, kernel_size=(5,5), activation='sigmoid')
        self.p2 = MaxPool2D(pool_size=(2,2), strides=2)

        self.flatten = Flatten()
        self.f1 = Dense(120, activation='sigmoid')
        self.f2 = Dense(84, activation='sigmoid')
        self.f3 = Dense(10, activation='softmax')

    def call(self, x):
        x = self.c1(x)
        x = self.p1(x)
        x = self.c2(x)
        x = self.p2(x)
        x = self.flatten(x)
        x = self.f1(x)
        x = self.f2(x)
        y = self.f3(x)
        return y

dat = DataSets()
(x_train, y_train), (x_test, y_test) = dat.load_cifar10()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = LeNet5()

history = tf_utils.model_train(model, "LeNet5", x_train, y_train, x_test, y_test)

model.summary()

file = open('./weighs.txt', 'w')
for v in model.trainable_variables:
    file.write(str(v.name) + '\n')
    file.write(str(v.shape) + '\n')
    file.write(str(v.numpy()) + '\n')
file.close()

tf_utils.history_show(history)

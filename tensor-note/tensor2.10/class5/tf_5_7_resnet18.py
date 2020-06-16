# -*- coding: utf-8 -*-

from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, Dense
from tf_5_1_data_set import DataSets
import tf_5_0_utils as tf_utils
import tensorflow as tf

class ResnetBlock(Model):
    def __init__(self, filters, strides=1, residual_path=False):
        super(ResnetBlock, self).__init__()
        self.filters = filters
        self.strides = strides
        self.residual_path = residual_path

        self.c1 = Conv2D(filters, (3, 3), strides=strides, padding='same', use_bias=False)
        self.b1 = BatchNormalization()
        self.a1 = Activation('relu')

        self.c2 = Conv2D(filters, (3, 3), strides=1, padding='same', use_bias=False)
        self.b2 = BatchNormalization()

        if residual_path:
            self.down_c1 = Conv2D(filters, (1, 1), strides=strides, padding='same', use_bias=False)
            self.down_b1 = BatchNormalization()

        self.a2 = Activation('relu')

    def call(self, inputs):
        residual = inputs
        x = self.c1(inputs)
        x = self.b1(x)
        x = self.a1(x)
        x = self.c2(x)
        y = self.b2(x)

        if self.residual_path:
            residual = self.down_c1(inputs)
            residual = self.down_b1(residual)
        out = self.a2(y + residual)
        return out

class ResNet18(Model):
    def __init__(self, block_list, initial_filters=64):
        '''构建RseNet神经网络
        param: block_list  [2,2,2,2] 4个block,每个block有2个卷积层
        '''
        super(ResNet18, self).__init__()
        self.num_blocks = len(block_list)
        self.block_list = block_list
        self.out_filters = initial_filters
        self.c1 = Conv2D(self.out_filters, (3, 3), strides=1, padding='same', use_bias=False)
        self.b1 = BatchNormalization()
        self.a1 = Activation('relu')
        self.blocks = tf.keras.models.Sequential()
        for block_id,layer_num in enumerate(block_list):  # 分别处理每个block
            for layer_id in range(layer_num):  # 分别处理每个卷积层
                if block_id != 0 and layer_id == 0:  # 除第一个block以外的每个block的输入进行下采样
                    block = ResnetBlock(self.out_filters, strides=2, residual_path=True)
                else:
                    block = ResnetBlock(self.out_filters, residual_path=False)
                self.blocks.add(block)
            self.out_filters *= 2
        self.p1 = tf.keras.layers.GlobalAveragePooling2D()
        self.f1 = Dense(10, activation='softmax', kernel_regularizer=tf.keras.regularizers.l2())

        def call(self, inputs):
            x = self.c1(inputs)
            x = self.b1(x)
            x = self.a1(x)
            x = self.blocks(x)
            x = self.p1(x)
            y = self.f1(x)
            return y

dat = DataSets()
(x_train, y_train), (x_test, y_test) = dat.load_cifar10()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = ResNet18([2, 2, 2, 2])

history = tf_utils.model_train(model, "ResNet18", x_train, y_train, x_test, y_test)

tf_utils.model_save(model)

tf_utils.history_show(history)

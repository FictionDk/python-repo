# -*- coding: utf-8 -*-

from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPool2D, Dense, GlobalAveragePooling2D
from tf_5_1_data_set import DataSets
import tf_5_0_utils as tf_utils
import tensorflow as tf

class ConvBNRelu(Model):
    def __init__(self, ch, kernelsz=3, strides=1, padding='same'):
        super(ConvBNRelu, self).__init__()
        self.model = tf.keras.models.Sequential([
            Conv2D(ch, kernelsz, strides=strides, padding=padding),
            BatchNormalization(),
            Activation('relu')
        ])

    def call(self, x):
        x = self.model(x, training=False)
        return x

class InceptionBlk(Model):
    def __init__(self, ch, strides=1):
        super(InceptionBlk, self).__init__()
        self.ch = ch
        self.strides = strides
        self.c1 = ConvBNRelu(ch, kernelsz=1, strides=strides)
        self.c2_1 = ConvBNRelu(ch, kernelsz=1, strides=strides)
        self.c2_2 = ConvBNRelu(ch, kernelsz=3, strides=1)  # ch个3*3的卷积核,步长为1,默认全0填充
        self.c3_1 = ConvBNRelu(ch, kernelsz=1, strides=strides)
        self.c3_2 = ConvBNRelu(ch, kernelsz=5, strides=1)
        self.p4_1 = MaxPool2D(3, strides=1, padding='same')
        self.c4_2 = ConvBNRelu(ch, kernelsz=1, strides=strides)

    def call(self, x):
        x1 = self.c1(x)
        x2_1 = self.c2_1(x)
        x2_2 = self.c2_2(x2_1)
        x3_1 = self.c3_1(x)
        x3_2 = self.c3_2(x3_1)
        x4_1 = self.p4_1(x)
        x4_2 = self.c4_2(x4_1)
        x = tf.concat([x1, x2_2, x3_2, x4_2], axis=3)  # 指定堆叠的深度,axix=channel
        return x

class Inception10(Model):
    def __init__(self, num_blocks, num_classes, init_ch=16, **kwargs):
        '''10层网络的精简InceptionNet
        Args:
            num_blocks  Block数量
            num_classes  数据集的分类
            init_ch
        '''
        super(Inception10, self).__init__(**kwargs)
        self.in_channels = init_ch
        self.out_channels = init_ch
        self.num_blocks = num_blocks
        self.init_ch = init_ch
        self.c1 = ConvBNRelu(init_ch)  # 16个3*3卷积核,步长为1,全零填充,BN操作,relu激活
        self.blocks = tf.keras.models.Sequential()
        # 4个Inception结构块顺序相连,每两个结成一个Block
        for block_id in range(num_blocks):
            for layer_id in range(2):  # 每一个Block中第一个块,卷积步长2,第二个卷积步长1
                if layer_id == 0:
                    block = InceptionBlk(self.out_channels, strides=2)  # 输出尺寸特征值减半
                else:
                    block = InceptionBlk(self.out_channels, strides=1)
                self.blocks.add(block)
            self.out_channels *= 2  # 加深输出特征图深度,保持特征抽取中信息的承载量一致
        self.p1 = GlobalAveragePooling2D()
        self.f1 = Dense(num_classes, activation='softmax')

    def call(self, x):
        x = self.c1(x)
        x = self.blocks(x)
        x = self.p1(x)
        y = self.f1(x)
        return y

dat = DataSets()
(x_train, y_train), (x_test, y_test) = dat.load_cifar10()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = Inception10(num_blocks=2, num_classes=10)

tf_utils.numpy_info_show(x_train)

history = tf_utils.model_train(model, "Inception10", x_train, y_train, x_test, y_test, batch_size=1024)

model.summary()

tf_utils.model_save(model)

tf_utils.history_show(history)

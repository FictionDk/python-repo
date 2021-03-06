# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import tensorflow as tf
import os

def history_show(history):
    '''模型训练过程可视化(pyplot实现)
    '''
    acc = history.history['sparse_categorical_accuracy']
    val_acc = history.history['val_sparse_categorical_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Training Acc')
    plt.plot(val_acc, label='Validation Acc')
    plt.title('Training and Validation Acc')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Training Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.legend()

    plt.show()

def model_train(model, conv_type, x_train, y_train, x_test, y_test, batch_size=32):
    '''模型训练
    Args:
        model: tensorflow.keras.Model 模型对象
        conv_type: string 卷积模型名称
        x_train, y_train, x_test, y_test: numpy 训练集和测试集
    '''
    adamax = tf.keras.optimizers.Adamax(lr=0.1)
    # adam = tf.keras.optimizers.Adam(lr=0.002)
    model.compile(optimizer=adamax,
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        metrics=['sparse_categorical_accuracy'])

    checkout_save_path = './checkout/CONV.ckpt'.replace('CONV', conv_type)

    if os.path.exists(checkout_save_path + '.index'):
        model.load_weights(checkout_save_path)

    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkout_save_path,
        save_weights_only=True,
        save_best_only=True)

    history = model.fit(x_train, y_train, batch_size=batch_size, epochs=10,
        validation_data=(x_test, y_test), validation_freq=1,callbacks=[cp_callback])

    model.summary()

    return history

def model_save(model):
    '''模型保存
    Args:
        model: tensorflow.keras.Model 模型对象
    '''
    file = open('./weighs.txt', 'w')
    for v in model.trainable_variables:
        file.write(str(v.name) + '\n')
        file.write(str(v.shape) + '\n')
        file.write(str(v.numpy()) + '\n')
    file.close()

def numpy_info_show(arr):
    print("数据类型:",type(arr))
    print("数组元素数据类型：",arr.dtype)
    print("数组元素总数：",arr.size)
    print("数组形状:",arr.shape)
    print("数组的维度数目:",arr.ndim)

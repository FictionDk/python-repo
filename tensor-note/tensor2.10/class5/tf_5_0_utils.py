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

def model_train(model, conv_type, x_train, y_train, x_test, y_test):
    '''模型训练
    Args:
        model: tensorflow.keras.Model 模型对象
        conv_type: string 卷积模型名称
        x_train, y_train, x_test, y_test: numpy 训练集和测试集
    '''
    model.compile(optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
        metrics=['sparse_categorical_accuracy'])

    checkout_save_path = './checkout/CONV.ckpt'.replace('CONV', conv_type)

    if os.path.exists(checkout_save_path + '.index'):
        model.load_weights(checkout_save_path)

    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkout_save_path,
        save_weights_only=True,
        save_best_only=True)

    history = model.fit(x_train, y_train, batch_size=32, epochs=10,
        validation_data=(x_test, y_test), validation_freq=1,callbacks=[cp_callback])

    return history

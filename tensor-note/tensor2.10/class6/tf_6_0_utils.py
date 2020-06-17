# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import tensorflow as tf
import os

def history_show(history):
    '''模型训练过程可视化(pyplot实现)
    '''
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.plot(loss, label='Training Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.show()

def predicted_show(model, x_test, sc, test_set):
    '''测试集输入模型进行预测并展示
    param: model , tf.keras.Sequential, 预测模型
    param: x_test
    parma: sc
    param: test_set
    '''
    predicted_stock_price = model.predict(x_test)
    # 对预测数据还原---从（0，1）反归一化到原始范围
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    # 对真实数据还原---从（0，1）反归一化到原始范围
    real_stock_price = sc.inverse_transform(test_set[60:])
    # 画出真实数据和预测数据的对比曲线
    plt.plot(real_stock_price, color='red', label='MaoTai Stock Price')
    plt.plot(predicted_stock_price, color='blue', label='Predicted MaoTai Stock Price')
    plt.title('MaoTai Stock Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('MaoTai Stock Price')
    plt.legend()
    plt.show()

def model_train(model, conv_type, x_train, y_train, x_test, y_test, batch_size=32):
    '''模型训练
    Args:
        model: tensorflow.keras.Model 模型对象
        conv_type: string 卷积模型名称
        x_train, y_train, x_test, y_test: numpy 训练集和测试集
    '''
    adamax = tf.keras.optimizers.Adamax(lr=0.002)
    # adam = tf.keras.optimizers.Adam(lr=0.002)
    model.compile(optimizer=adamax, loss='mean_squared_error')

    checkout_save_path = './checkout/CONV.ckpt'.replace('CONV', conv_type)

    if os.path.exists(checkout_save_path + '.index'):
        model.load_weights(checkout_save_path)

    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkout_save_path,
        save_weights_only=True,
        save_best_only=True,
        monitor='val_loss')

    history = model.fit(x_train, y_train, batch_size=batch_size, epochs=50,
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

# -*- coding: utf-8 -*-
from PIL import Image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot as plt
import numpy as np
import tensorflow as tf
import os

train_path = 'D:\\Resource\\tensor_doc\\exam\\fashion_image_label\\fashion_train_jpg_60000\\'
train_txt = 'D:\\Resource\\tensor_doc\\exam\\fashion_image_label\\fashion_train_jpg_60000.txt'

test_path = 'D:\\Resource\\tensor_doc\\exam\\fashion_image_label\\fashion_test_jpg_10000\\'
test_txt = 'D:\\Resource\\tensor_doc\\exam\\fashion_image_label\\fashion_test_jpg_10000.txt'

checkpoint_save_path = "./checkpoint/fashion.ckpt"

fashion_image_label_path = './fashion_image_label/'

x_train_save_path = './fashion_image_label/fashion_x_train.npy'
y_train_save_path = './fashion_image_label/fashion_y_train.npy'

x_test_save_path = './fashion_image_label/fashion_x_test.npy'
y_test_save_path = './fashion_image_label/fashion_y_test.npy'

need_image_gen = False

def generateds(path, txt):
    f = open(txt, 'r')
    contents = f.readlines()
    f.close()
    x, y_ = [], []
    for i,content in enumerate(contents):
        value = content.split()
        img_path = path + value[0]
        img = Image.open(img_path)
        img = np.array(img.convert('L'))
        img = img / 255.
        x.append(img)
        y_.append(value[1])
        if i % 500 == 0:
            print(" %d is loading in %s" % (i, txt))

    x = np.array(x)
    y_ = np.array(y_)
    y_ = y_.astype(np.int64)
    return x, y_

if os.path.exists(x_train_save_path) and os.path.exists(y_train_save_path) and os.path.exists(x_test_save_path) and os.path.exists(y_test_save_path):
    x_train_save = np.load(x_train_save_path)
    y_train = np.load(y_train_save_path)
    x_test_save = np.load(x_test_save_path)
    y_test = np.load(y_test_save_path)
    x_train = np.reshape(x_train_save, (len(x_train_save), 28, 28))
    x_test = np.reshape(x_test_save, (len(x_test_save), 28, 28))
else:
    x_train, y_train = generateds(train_path, train_txt)
    x_test, y_test = generateds(test_path, test_txt)
    os.makedirs(fashion_image_label_path)
    x_train_save = np.reshape(x_train, (len(x_train), -1))
    x_test_save = np.reshape(x_test, (len(x_test), -1))
    np.save(x_train_save_path, x_train_save)
    np.save(y_train_save_path, y_train)
    np.save(x_test_save_path, x_test_save)
    np.save(y_test_save_path, y_test)

if need_image_gen:
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
    image_gen_train = ImageDataGenerator(
        rescale=1. / 1.,
        rotation_range=45,
        width_shift_range=.15,
        height_shift_range=.15,
        horizontal_flip=True,
        zoom_range=0.5
    )
    image_gen_train.fit(x_train)

if need_image_gen:
    input_shape = (28,28,1)
else:
    input_shape = (28,28)

model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=input_shape),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['sparse_categorical_accuracy'])

checkpoint_save_path = "./checkpoint/fashion.ckpt"
if os.path.exists(checkpoint_save_path + '.index'):
    model.load_weights(checkpoint_save_path)

cp_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_save_path,
    save_weights_only=True,
    monitor='val_loss',
    save_best_only=True)

if need_image_gen:
    history = model.fit(image_gen_train.flow(x_train, y_train, batch_size=32), epochs=50,
        validation_data=(x_test, y_test),
        validation_freq=1,
        callbacks=[cp_callback])
else:
    history = model.fit(x_train, y_train, batch_size=32, epochs=50,
        validation_data=(x_test, y_test),
        validation_freq=1,
        callbacks=[cp_callback])

model.summary()

print(model.trainable_variables)

weights_file = open('./checkpoint/weights.txt', 'w')
for v in model.trainable_variables:
    weights_file.write(str(v.name) + '\n')
    weights_file.write(str(v.shape) + '\n')
    weights_file.write(str(v.numpy()) + '\n')
weights_file.close()

acc = history.history['sparse_categorical_accuracy']
val_acc = history.history['val_sparse_categorical_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validaion Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.show()

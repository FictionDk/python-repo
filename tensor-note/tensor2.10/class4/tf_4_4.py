# -*- coding: utf-8 -*-
import tensorflow as tf
import os
import numpy as np

np.set_printoptions(threshold=np.inf)

mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(28,28)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['sparse_categorical_accuracy'])

checkpoint_save_path = "./checkpoint/mnist.ckpt"
if os.path.exists(checkpoint_save_path + '.index'):
    model.load_weights(checkpoint_save_path)

cp_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_save_path,
    save_weights_only=True,
    monitor='val_loss',
    save_best_only=True)

history = model.fit(x_train, y_train, batch_size=32, epochs=5,
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

# -*- coding: utf-8 -*-

from tf_6_1_dataset import StockDataSet
from tensorflow.keras.layers import Dropout, Dense, SimpleRNN
import tensorflow as tf
import tf_6_0_utils as utils

model = tf.keras.Sequential([
    SimpleRNN(80, return_sequences=True),
    Dropout(0.2),
    SimpleRNN(100),
    Dropout(0.2),
    Dense(1)])

maotai_stock = StockDataSet()
(x_train, y_train), (x_test, y_test) = maotai_stock.load_date()

history = utils.model_train(model, "RNNSimple", x_train, y_train, x_test, y_test)

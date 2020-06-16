# -*- coding: utf-8 -*-

from sklearn.preprocessing import MinMaxScaler
import tf_6_0_utils as tf_utils
import pandas as pd
import numpy as np

class StockDataSet(object):
    def __init__(self, stock_name="maotai"):
        self.stock = stock_name

    def load_date(self, stock_name=None):
        if stock_name is None:
            stock_name = self.stock
        if stock_name == "maotai":
            return self._load_stock()
        else:
            raise RuntimeError("no avalable stock data")

    def _load_stock(self, stock_num="SH600519"):
        stock_csv = pd.read_csv('./assert/SH600519.csv')
        training_set = stock_csv.iloc[0:2426 - 300, 2:3].values
        test_set = stock_csv.iloc[2426 - 300:, 2:3].values

        sc = MinMaxScaler(feature_range=(0,1))
        training_set_scaled = sc.fit_transform(training_set)
        test_set = sc.transform(test_set)

        x_train, y_train, x_test, y_test = [], [], [], []
        for i in range(60, len(training_set_scaled)):
            x_train.append(training_set_scaled[i - 60:i,0])
            y_train.append(training_set_scaled[i, 0])

        np.random.seed(7)
        np.random.shuffle(x_train)
        np.random.seed(7)
        np.random.shuffle(y_train)
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], 60, 1))

        for i in range(60, len(test_set)):
            x_test.append(test_set[i - 60:i, 0])
            y_test.append(test_set[i, 0])
        x_test, y_test = np.array(x_test), np.array(y_test)
        x_test = np.reshape(x_test, (x_test.shape[0], 60, 1))
        return (x_train, y_train),(x_test, y_test)

def test():
    dat = StockDataSet()
    (x_train, y_train),(x_test, y_test) = dat.load_date()
    tf_utils.numpy_info_show(x_train)
    tf_utils.numpy_info_show(x_test)

test()

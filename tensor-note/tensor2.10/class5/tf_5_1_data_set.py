# -*- coding: utf-8 -*-
from PIL import Image
from matplotlib import pyplot as plt
# import tensorflow as tf
import numpy as np
import os

np.set_printoptions(threshold=np.inf)

# cifar10 = tf.keras.datasets.cifar10
# (x_train, y_train), (x_test, y_test) = cifar10.load_data()

img_path = 'D:\\Resource\\tensor_doc\\cifar-10\\'
base_dir = 'D:\\Resource\\tensor_doc\\exam\\fashion_image_label\\'

class DataSets(object):
    def __init__(self, img_path=img_path, save_name='cifar10'):
        self.path = img_path
        self.name = save_name
        self.x_train_save_path = self.build_path('x','train')
        self.y_train_save_path = self.build_path('y', 'train')
        self.x_test_save_path = self.build_path('x', 'test')
        self.y_test_save_path = self.build_path('y', 'test')

    def load_cifar10(self):
        if os.path.exists(self.x_train_save_path) and os.path.exists(self.y_train_save_path) and os.path.exists(self.x_test_save_path) and os.path.exists(self.y_test_save_path):
            x_train_save = np.load(self.x_train_save_path)
            y_train = np.load(self.y_train_save_path)
            x_test_save = np.load(self.x_test_save_path)
            y_test = np.load(self.y_test_save_path)
            x_train = np.reshape(x_train_save, (len(x_train_save), 32, 32, 3))
            x_test = np.reshape(x_test_save, (len(x_test_save), 32, 32, 3))
        else:
            x_train, y_train = self.generateds(img_path, "train")
            x_test, y_test = self.generateds(img_path, "test")
            os.makedirs(self.build_path(None,None))
            x_train_save = np.reshape(x_train, (len(x_train), -1))
            x_test_save = np.reshape(x_test, (len(x_test), -1))
            np.save(self.x_train_save_path, x_train_save)
            np.save(self.y_train_save_path, y_train)
            np.save(self.x_test_save_path, x_test_save)
            np.save(self.y_test_save_path, y_test)
        return (x_train, y_train), (x_test, y_test)

    def build_path(self, axis, type):
        if axis is None:
            return './' + self.name + '/'
        return "./" + self.name + "/" + self.name + '_AXIS_TYPE.npy'.replace('AXIS',axis).replace('TYPE',type)

    def categories(self):
        '''获取所有种类列表
        '''
        categories = os.listdir(self.path + "train")
        return categories

    def generateds(self, path, txt):
        '''根据路径组合内容
        '''
        categories = self.categories()
        x, y_ = [], []
        total_count = 0
        for i,category in enumerate(categories):
            dir_fullpath = self.path + txt + '\\' + category
            img_names = os.listdir(dir_fullpath)
            for img_name in img_names:
                img_path = dir_fullpath + '\\' + img_name
                img = Image.open(img_path)
                img = np.array(img.convert('RGB'))
                # img = img / 255.
                x.append(img)
                y_.append(i)
                total_count += 1
                if total_count % 500 == 0:
                    print("current is %s , img_path is %s" % (img_name, img_path))
                    print(" %d is loading in %s" % (total_count, txt))

        x = np.array(x)
        y_ = np.array(y_)
        y_ = y_.astype(np.int64)
        return x, y_

class FashinDataSet(object):
    def __init__(self, img_path=base_dir, save_name='fashion'):
        self.path = img_path
        self.name = save_name
        self.x_train_save_path = self.build_path('x','train')
        self.y_train_save_path = self.build_path('y', 'train')
        self.x_test_save_path = self.build_path('x', 'test')
        self.y_test_save_path = self.build_path('y', 'test')

    def _generateds(self, path, txt):
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

    def load_fashion(self):
        if os.path.exists(self.x_train_save_path) and os.path.exists(self.y_train_save_path) and os.path.exists(self.x_test_save_path) and os.path.exists(self.y_test_save_path):
            x_train_save = np.load(self.x_train_save_path)
            y_train = np.load(self.y_train_save_path)
            x_test_save = np.load(self.x_test_save_path)
            y_test = np.load(self.y_test_save_path)
            x_train = np.reshape(x_train_save, (len(x_train_save), 28, 28, 1))
            x_test = np.reshape(x_test_save, (len(x_test_save), 28, 28, 1))
        else:
            train_jpg_dir, train_txt_path = self._build_source_path('train')
            text_jpg_dir, test_txt_path = self._build_source_path('test')
            x_train, y_train = self._generateds(train_jpg_dir, train_txt_path)
            x_test, y_test = self._generateds(text_jpg_dir, test_txt_path)
            os.makedirs(self.build_path(None,None))
            x_train_save = np.reshape(x_train, (len(x_train), -1))
            x_test_save = np.reshape(x_test, (len(x_test), -1))
            np.save(self.x_train_save_path, x_train_save)
            np.save(self.y_train_save_path, y_train)
            np.save(self.x_test_save_path, x_test_save)
            np.save(self.y_test_save_path, y_test)
        return (x_train, y_train), (x_test, y_test)

    def _build_source_path(self, source_type):
        if source_type is 'train':
            jpg_dir,txt_path = self.path + 'fashion_train_jpg_60000\\',base_dir + '\\fashion_train_jpg_60000.txt'
        elif source_type is 'test':
            jpg_dir,txt_path = self.path + 'fashion_test_jpg_10000\\',base_dir + '\\fashion_test_jpg_10000.txt'
        else:
            raise RuntimeError("err source_type in _build_source_path()")
        return jpg_dir,txt_path

    def build_path(self, axis, type):
        if axis is None:
            return './' + self.name + '/'
        return "./" + self.name + "/" + self.name + '_AXIS_TYPE.npy'.replace('AXIS',axis).replace('TYPE',type)

def test_cifar():
    dat = DataSets(img_path,'cifar10')
    (x_train, y_train), (x_test, y_test) = dat.load_cifar10()
    plt.imshow(x_train[100])
    plt.show()
    print("x_train[100]: \n", x_train[100])
    print("y_train[100]:", y_train[100])
    print("x_test.shape: ", x_test.shape)

def test_fashion():
    dat = FashinDataSet()
    (x_train, y_trian), (x_test, y_test) = dat.load_fashion()
    plt.imshow(x_train[100])
    plt.show()

# test_fashion()

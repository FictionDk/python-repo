# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from skimage import io,transform
from pylab import mpl

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

def load_image(path):
    fig = plt.figure("Centre and Resize")
    img = io.imread(path)
    img = img / 255.0

    ax0 = fig.add_subplot(131)
    ax0.set_xlabel(u'Original Pictrue')
    ax0.imshow(img)

    # print(img.shape)  # (width,length,channel)

    short_edge = min(img.shape[:2])
    print("short_edge: ",short_edge)
    y = (img.shape[0] - short_edge) / 2
    x = (img.shape[1] - short_edge) / 2
    crop_img = img[int(y):int(y + short_edge), int(x):int(x + short_edge)]

    ax1 = fig.add_subplot(132)
    ax1.set_xlabel(u'Centre Pictrue')
    ax1.imshow(crop_img)

    re_img = transform.resize(crop_img,(224,224))

    ax2 = fig.add_subplot(133)
    ax2.set_xlabel(u'Resize Pictrue')
    ax2.imshow(re_img)

    img_ready = re_img.reshape((1,224,224,3))
    return img_ready

def percent(val):
    return '%.2f%%' % (val * 100)

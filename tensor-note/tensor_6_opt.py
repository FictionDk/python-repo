# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# tf.shape(a) --返回维度
def tf_shape():
    x = tf.constant([[1,2,4],[7,9,0]])
    y = [[[1,2],[2,3],[4,5]]]
    z = np.arange(24).reshape([2,3,4])
    with tf.Session() as sess:
        print(sess.run(tf.shape(x)))
        print(sess.run(tf.shape(y)))
        print(sess.run(tf.shape(z)))

def tf_split():
    x = np.arange(24).reshape([8,-1])
    print(x)
    tx = tf.constant(x)
    # tx-被切值;[3,3,2]-怎么切,将第0个维度的8行,分别切成3,3,2;0-切的维度
    split_0,split_1,split_2 = tf.split(tx,[3,3,2],0)
    with tf.Session() as sess:
        print(sess.run(tf.shape(split_1)))
        print(sess.run(tf.shape(split_2)))

def tf_variable_scope():
    with tf.variable_scope("a"):
        with tf.variable_scope("b"):
            c = tf.get_variable("c",[0])
            print(c.name)

def main():
    # tf_shape()
    # tf_split()
    tf_variable_scope()

if __name__ == '__main__':
    main()

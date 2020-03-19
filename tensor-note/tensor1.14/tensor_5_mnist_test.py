# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import numpy as np
import os
from tensorflow.examples.tutorials.mnist import input_data
import tensor_5_mnist_forward as mnist_forward
import tensor_5_mnist_backward as mnist_backward
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


TEST_INTERVAL_SECS = 8

def test(mnist):
    with tf.Graph().as_default() as g:
        print("type(g) is ",type(g))
        x = tf.placeholder(tf.float32,[
            mnist.test.num_examples,
            mnist_forward.IMAGE_SIZE,
            mnist_forward.IMAGE_SIZE,
            mnist_forward.NUM_CHANNELS])
        y_ = tf.placeholder(tf.float32,[None,mnist_forward.OUTPUT_NODE])
        y = mnist_forward.forward(x,False,None)

        ema = tf.train.ExponentialMovingAverage(mnist_backward.MOVING_AVERAGE_DECAY)
        ema_restore = ema.variables_to_restore()
        saver = tf.train.Saver(ema_restore)

        correct_prediction = tf.equal(tf.argmax(y,1),tf.argmax(y_,1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))

        while True:
            with tf.Session() as sess:
                ckpt = tf.train.get_checkpoint_state(mnist_backward.MODEL_SAVE_PATH)
                if ckpt and ckpt.model_checkpoint_path:
                    saver.restore(sess,ckpt.model_checkpoint_path)

                    global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    reshaped_x = np.reshape(mnist.test.images,(
                        mnist.test.num_examples,
                        mnist_forward.IMAGE_SIZE,
                        mnist_forward.IMAGE_SIZE,
                        mnist_forward.NUM_CHANNELS))
                    accuracy_score = sess.run(accuracy,feed_dict={x:reshaped_x,y_:mnist.test.labels})
                    print("After %s training step(s), test accuracy = %g." % (global_step,accuracy_score))
                else:
                    print("No checkpoint file found in path.")
                    return
            time.sleep(TEST_INTERVAL_SECS)

def main():
    mnist = input_data.read_data_sets("./data/",one_hot=True)
    test(mnist)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import os
import tensorflow.compat.v1 as tf
import tensor_5_mnist_forward as forward
import tensor_5_mnist_backward as backward
from PIL import Image
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def restore_model(pic_arr):
    print(pic_arr.shape)
    with tf.Graph().as_default() as tg:
        print("type: %s " % (type(tg)))
        x = tf.placeholder(tf.float32,[
            1,
            forward.IMAGE_SIZE,
            forward.IMAGE_SIZE,
            forward.NUM_CHANNELS])

        y = forward.forward(x,False,None)
        pre_val = tf.argmax(y,1)

        variable_averages = tf.train.ExponentialMovingAverage(backward.MOVING_AVERAGE_DECAY)
        variables_to_restore = variable_averages.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)

        with tf.Session() as sess:
            ckpt = tf.train.get_checkpoint_state(backward.MODEL_SAVE_PATH)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess,ckpt.model_checkpoint_path)
                reshaped_pic = np.reshape(pic_arr,(
                    1,
                    forward.IMAGE_SIZE,
                    forward.IMAGE_SIZE,
                    forward.NUM_CHANNELS))
                pre_val = sess.run(pre_val,feed_dict={x:reshaped_pic})
                return pre_val
            else:
                print("No checkpoint file found.")
                return -1

def pre_pic(pic_name):
    img = Image.open(pic_name).convert('L')
    re_id = img.resize((28,28),Image.ANTIALIAS)
    im_arr = np.array(re_id)
    threshold = 50
    for i in range(28):
        for j in range(28):
            im_arr[i][j] = 255 - im_arr[i][j]
            if im_arr[i][j] < threshold:
                im_arr[i][j] = 0
            else:
                im_arr[i][j] = 255
    nm_arr = im_arr.astype(np.float32)
    img_ready = np.multiply(nm_arr, 1.0 / 255.0)
    return img_ready

def main():
    test_num = input("Input the number of test pictures : ")
    for i in range(int(test_num)):
        test_pic = input("The path of test picture : ")
        test_pic_arr = pre_pic(test_pic)
        pre_val = restore_model(test_pic_arr)
        print("This prediction number is : ",pre_val)

if __name__ == "__main__":
    main()

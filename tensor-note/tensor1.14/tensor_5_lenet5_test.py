# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import tensor_5_lenet5_forward as lenet5_forward
import tensor_5_lenet5_backward as lenet5_backward
import tensor_5_lenet5_generateds as lenet5_generateds
import time
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
TEST_INTERVAL_SECS = 8
test_num_examples = 10000

def test():
    with tf.Graph().as_default() as g:
        print("type(g) is ",type(g))
        x = tf.placeholder(tf.float32,[
            test_num_examples,
            lenet5_forward.IMAGE_SIZE,
            lenet5_forward.IMAGE_SIZE,
            lenet5_forward.NUM_CHANNELS])
        y_ = tf.placeholder(tf.float32,[None,lenet5_forward.OUTPUT_NODE])
        y = lenet5_forward.forward(x,False,None)

        ema = tf.train.ExponentialMovingAverage(lenet5_backward.MOVING_AVERAGE_DECAY)
        ema_restore = ema.variables_to_restore()
        saver = tf.train.Saver(ema_restore)

        correct_prediction = tf.equal(tf.argmax(y,1),tf.argmax(y_,1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))

        while True:
            img_batch,label_batch = lenet5_generateds.get_tfRecord(test_num_examples,False)
            with tf.Session() as sess:
                ckpt = tf.train.get_checkpoint_state(lenet5_backward.MODEL_SAVE_PATH)
                if ckpt and ckpt.model_checkpoint_path:
                    saver.restore(sess,ckpt.model_checkpoint_path)
                    global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]

                    coord = tf.train.Coordinator()
                    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

                    xs,ys = sess.run([img_batch,label_batch])

                    accuracy_score = sess.run(accuracy,feed_dict={x:xs,y_:ys})
                    print("After %s training step(s), test accuracy = %g." % (global_step,accuracy_score))

                    coord.request_stop()
                    coord.join(threads)
                else:
                    print("No checkpoint file found in path.")
                    return
            time.sleep(TEST_INTERVAL_SECS)

def main():
    test()

if __name__ == '__main__':
    main()

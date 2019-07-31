# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 设损失函数 loss=(w+1)^2,令w初值为5,反向传播求解最优解;
# w=-1 loss=0
def main():
    w = tf.Variable(tf.constant(5,dtype=tf.float32))
    loss = tf.square(w + 1)
    # 当学习率过大,损失函数不收敛; 当学习率国小,损失函数收敛慢
    train_step = tf.train.GradientDescentOptimizer(0.2).minimize(loss)
    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        for i in range(40):
            sess.run(train_step)
            w_val = sess.run(w)
            loss_val = sess.run(loss)
            print("After %s steps: w is %f, loss is %f" % (i,w_val,loss_val))

if __name__ == "__main__":
    main()

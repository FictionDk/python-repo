# -*- coding: utf-8 -*-
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 交叉熵
# eg: 二分类,已知答案 y_=(1,0) 预测y1=(0.6,0.4),y2=(0.8,0.2), 哪个更接及y
# H1(1,0),(0.6,0.4)=-(1*log0.6+0*log0.4) ~ 0.222
# H2(1,0),(0.8,0.2)=-(1*log0.8+0*log0.2) ~ 0.097
# => y2更接近
# ce=-tf.reduce_mean(y_*tf.log(tf.clip_by_value(y,1e-12,1.0)))
# softmax()函数 --> 满足概率分布要求

# ce=tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y,labels=tf.argmax(y_,1))
# cem=tf.reduce_mean(ce)

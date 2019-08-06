## tensor-note

> tensorflow 笔记

课程地址: [人工智能实践：Tensorflow笔记(曹建)](http://www.icourse163.org/learn/PKU-1002536002?tid=1206591210#)

代码参考课程代码,转由python3.7+tensor1.14+numpy1.16实现


### 4.1 mnist手写训练

#### 4.1.1 mnist数据集

```
# IPython
# 导入数据集
In[]: from tensorflow.contrib.learn.python.learn.datasets.mnist
import read_data_sets
In[]: mnist_data = read_data_sets("./data/",one_hot=True)
# 查看训练集第0张图像素
In[]: mnist_data.train.images[0]
# 查看训练集第0张图标签:
In[]: mnist_data.train.labels[0]
In[]: mnist_data.train # 训练集
                .validation # 验证集
                .test # 测试集
```

#### 4.1.2 tf常用函数

1. `tf.get_collection("")`从集合中取出全部变量生成一个列表
2. 张量计算
```
# IPython
import tensorflow.compat.v1 as tf
x = tf.constant([[1,2],[2,3]])
y = tf.constant([[1,1],[2,2]])
z = tf.add(x,y)
print(z)
# OUT[1]: Tensor("Add:0",shape=(2,2),dtype=int32)
with tf.Session() as sess:
    print(sess.run(z))
# OUT[2]:
[[2,3]
 [4,5]]
```
3. 张量转换:
```
import numpy as np
A = tf.convert_to_tensor(np.array[[1,1,2,4],[3,4,8,5]])
print(A)
# OUT[3]: Tensor("Const_3:0",shape(2,4),dtype=int32)
b = tf.cast(A,tf.float32)
print(b)
# OUT[3]: Tensor("Const:0",shape(2,4),dtype=float32)
with tf.Session() as sess:
    print(sess.run(b))
# OUT[4]:
[[1. 1. 2. 4.]
 [3. 4. 8. 5.]]
```

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

### 5.1 卷积基础

#### 5.1.1 全连接NN

每个神经元与前后相邻层的每一个神经元都有连接关系，输入是特征，输出为预测的结果  

参数个数：∑（前层 × 后层 + 后层）  

#### 5.1.2 卷积

卷积是一种有效提取图片特征的方法。一般用一个正方形卷积核，遍历图片上的每一个像素点。图片与卷积核重合区域内相对应的每一个像素值乘卷积核内相对应点的权重，然后求和，再加上偏置后，最后得到输出图片中的一个像素值。 

输出图片边长=（输入图片边长–卷积核长+1）/步长，
（ 5 – 3 + 1）/ 1 = 3，输出图片是 3x3 的分辨率，用了 1 个卷积核，输出深度是 1，最后输出的是 3x3x1 的图片。
`(32 - 5 + 1) / 1 = 28`

全0填充:  
在输入图片周围进行全零填充，这样可以保证输出图片的尺寸和输入图片一致。  

#### 5.1.3 池化Pooling

最大池化: `tf.nn.max_pool`  
平均池化: `tf.nn.avg_pool`  
池化参数: 
```
pool = tf.nn.max_pool(
    输入描述: eg. [batch(批处理数量),28(行分辨率),28(列分辨率),6(通道数)],
    池化核描述: eg. [1(默认),2(行分辨率),2(列分辨率),1(默认)],
    池化核滑动步长: eg. [1,2(行步长),2(列步长),1],
    是否全0填充: eg. padding='SAME'(用0填充,VALID不填充)
)
```

全0填充池化后输出尺寸=输入尺寸/步长=28/2=14

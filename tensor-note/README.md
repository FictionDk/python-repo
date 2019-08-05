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

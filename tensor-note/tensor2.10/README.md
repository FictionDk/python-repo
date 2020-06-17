## tensor-note

### 第四讲 神经网络八股功能扩展

1. 自制数据集,解决本领域应用
2. 数据增强,扩充数据集
3. 断点续训,存储模型
4. 参数提取,把参数存入文本
5. acc/loss可视化,查看训练效果
6. 应用程序,给图识物

#### 数据增强

```python
x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)  # 需要四维数据, 最后1 表示图片颜色通道
x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
image_gen_train = ImageDataGenerator(
    rescale=1. / 1.,
    rotation_range=45,
    width_shift_range=.15,
    height_shift_range=.15,
    horizontal_flip=True,
    zoom_range=0.5
)
image_gen_train.fit(x_train)

history = model.fit(image_gen_train.flow(x_train, y_train, batch_size=32), epochs=50,
    validation_data=(x_test, y_test),
    validation_freq=1,
    callbacks=[cp_callback])
```

#### acc/loss可视化

- 训练集loss: loss
- 测试集loss: val_loss
- 训练集准确率: sparse_categorical_acc
- 测试集准确率: val_sparse_categorical_acc

### 第五讲 全连接神经网络

#### 卷积计算

1. 一种有效的提取图像特征的方法
2. 一般使用正方形的卷积核,按指定步长,在输入特征图上滑动遍历特征图中每一个像素点
3. 每一个步长,卷积核会与输入特征图出现重合区域,重合区域对应的元素相乘,求和再加上偏置项得输出的特征像素点
4. 输入特征图的深度(channel数),决定当前层卷积核的深度
5. 当前层卷积核的个数,决定当前层输出特征图的深度

#### 卷积神经网络

1. 感受野(Receptive Field): 卷积神经网络各输出特征图中的每个像素点,在原始输入图片上映射区域的大小
2. TF描述卷积层
    ```python
    tk.keras.layers.Conv2D(
        filters=卷积核个数,
        kernel_size=卷积核尺寸 核高h*核宽w,
        strides=滑动步长,横纵相同写步长整数,或(纵向步长h,横向步长w), 默认1
        padding='same' or 'valid', same全零填充,模拟valid,
        activation='relu' or 'sigmoid' or 'tanh' or 'softmax', 如有BN此处可忽略,
        input_shape=(高,宽,通道数) 输入特征图维度, 可省略)
    ```
3. 批标准化: 使数据符合0均值, 1为标准差的分布, 位于卷积层之后, 激活层之前
4. 池化: 减少特征数据量, 最大池化可提取图片纹理, 均值池化可保留背景特征
    ```python
    tf.layers.MaxPool2D(
        pool_size=(2,2), # 池化核尺寸,正方形可直接写长整数
        strides=2, # 池化步长,默认pool_size
        padding='same' # same:全零填充, 模拟valid
        )
    tf.layers.AveragePooling2D(
        pool_size=(2,2), # 池化核尺寸,正方形可直接写长整数
        strides=2, # 池化步长,默认pool_size
        padding='same' # same:全零填充, 模拟valid
        )
    ```
5. 舍弃: 为防止过拟合,讲一部分神经元按一定的概率从神经网络中暂时舍弃,使用时恢复连接

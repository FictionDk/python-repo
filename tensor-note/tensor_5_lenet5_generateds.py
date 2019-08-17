# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf
from PIL import Image
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
'''
将cifar-10图片制作成tfrecords文件
'''

# 需要读取的源图片文件夹(自定义)
image_train_path = "D:\\Resource\\tensor\\cifar-10\\train"
image_test_path = "D:\\Resource\\tensor\\cifar-10\\test"
# 需要保存生成的tfrecords文件
tfRecord_train = './data/cifar10_train.tfrecords'
tfRecord_test = './data/cifar10_test.tfrecords'
# 基础数据文件夹
data_path = './data'

def write_tfRecord(tfRecord_name,image_path):
    writer = tf.python_io.TFRecordWriter(tfRecord_name)
    types = os.listdir(image_path)
    print(types)
    for index,typ in enumerate(types):
        img_file_paths = os.path.join(image_path,typ)
        for img_file_path in os.listdir(img_file_paths):
            img = Image.open(os.path.join(image_path,typ,img_file_path))
            img_row = img.resize((32,32)).tobytes()
            labels = [0] * 10
            labels[index] = 1

            example = tf.train.Example(features=tf.train.Features(feature={
                'img_raw': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_row])),
                'label': tf.train.Feature(int64_list=tf.train.Int64List(value=labels))}))
            writer.write(example.SerializeToString())
        print("Index(%d) of types is %s ." % (index,typ))
    writer.close()
    print("Write tf record %s successful" % tfRecord_name)

def generate_tfRecord():
    is_exists = os.path.exists(data_path)
    if not is_exists:
        os.makedirs(data_path)
        print("%s was created successful" % data_path)
    write_tfRecord(tfRecord_train,image_train_path)
    write_tfRecord(tfRecord_test,image_test_path)

def read_tfRecord(tfRecord_path):
    filename_queue = tf.train.string_input_producer(
        [tfRecord_path],shuffle=True)
    reader = tf.TFRecordReader()
    _,serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(serialized_example,
        features={'label': tf.FixedLenFeature([10],tf.int64),
                'img_raw': tf.FixedLenFeature([],tf.string)})
    img = tf.decode_raw(features['img_raw'],tf.uint8)
    img = tf.reshape(img,[32,32,3])
    img = tf.cast(img,tf.float32) * (1.0 / 255)
    label = tf.cast(features['label'],tf.float32)
    return img,label

def check_tfRecord():
    check_path = "D:\\Resource\\tensor\\cifar-10\\check"
    is_exists = os.path.exists(check_path)
    if not is_exists:
        os.makedirs(check_path)
    # img_batch,label_batch = get_tfRecord(100)
    img_batch,label_batch = read_tfRecord(image_test_path)
    with tf.Session() as sess:
        init_op = tf.global_variables_initializer()
        sess.run(init_op)
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)
        for i in range(100):

            print("%d start ...." % i)
            example,lab = sess.run([img_batch,label_batch])
            print(lab.size)
            print(example.shape)
            img = Image.fromarray(example,mode='RGB')
            img_path = os.join(check_path,str(lab) + '.jpg')
            img.save(img_path)

        coord.request_stop()
        coord.jon(threads)

def get_tfRecord(num,isTrain=True):
    if isTrain:
        tfRecord_path = tfRecord_train
    else:
        tfRecord_path = tfRecord_test
    img,label = read_tfRecord(tfRecord_path)
    img_batch,label_batch = tf.train.shuffle_batch([img,label],
        batch_size=num,
        num_threads=2,
        capacity=1000,
        min_after_dequeue=700)
    img_batch = tf.cast(img_batch,tf.float32)
    return img_batch,label_batch

# 根据lable标签,返回类别名称
def get_typename(index):
    types = os.listdir(image_test_path)
    if index > len(types):
        return "Unknow"
    else:
        return types[index]

def main():
    # generate_tfRecord()
    check_tfRecord()

if __name__ == '__main__':
    main()

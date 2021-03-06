import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

# 모델에 대한 정의
class Model:
    # 생성자
    def __init__(self, sess, name):
        self.sess = sess
        self.name = name
        # 생성과 동시에 호출
        self._build_net()

    # 모델 만들기
    def _build_net(self):
        with tf.variable_scope(self.name):

            self.keep_prob = tf.placeholder(tf.float32)

            # input
            self.X = tf.placeholder(tf.float32, [None, 28 * 28])
            X_img = tf.reshape(self.X, [-1, 28, 28, 1])
            # output
            self.Y = tf.placeholder(tf.float32, [None, 10])

            W1 = tf.Variable(tf.random_normal([3, 3, 1, 32], stddev=0.01))
            L1 = tf.nn.conv2d(X_img, W1, strides=[1, 1, 1, 1], padding='SAME')
            L1 = tf.nn.relu(L1)
            L1 = tf.nn.max_pool(L1, strides=[1, 2, 2, 1], ksize=[1, 2, 2, 1], padding='SAME')

            # Layer2
            # img = (?, 14, 14, 32)
            # conv = (?, 14, 14, 64)
            # pool = (?, 7, 7, 64) (, , , number of filters)
            # reshape = (?, 3136)
            W2 = tf.Variable(tf.random_normal([3, 3, 32, 64], stddev=0.01))
            L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')
            L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
            L2 = tf.reshape(L2, [-1, 7 * 7 * 64])  # 펼치기

            # 가설
            W3 = tf.get_variable("W3", shape=[7 * 7 * 64, 10], initializer=tf.contrib.layers.xavier_initializer())
            b = tf.Variable(tf.random_normal([10]))
            self.logits = tf.matmul(L2, W3) + b

            # 비용함수 계산
            self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.logits, labels=self.Y))
            self.optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(self.cost)

            correct_prediction = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.Y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    def predict(self, x_test, keep_prob=1.0):
        return self.sess.run(self.logits
            , feed_dict={self.X: x_test, self.keep_prob: keep_prob})

    def get_accuracy(self, x_test, y_test, keep_prop=1.0):
        return self.sess.run(self.accuracy
            , feed_dict={self.X: x_test, self.Y: y_test, self.keep_prob: keep_prop})

    def train(self, x_data, y_data, keep_prob=0.7):
        return self.sess.run([self.cost, self.optimizer]
            , feed_dict={self.X: x_data, self.Y: y_data, self.keep_prob: keep_prob})


tf.set_random_seed(777)
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

sess = tf.Session()
m1 = Model(sess, "m1")

sess.run(tf.global_variables_initializer())

print("학습시작!!!")

training_epochs = 1
batch_size = 100

for epoch in range(training_epochs):
    avg_cost = 0;
    total_batch = int(mnist.train.num_examples / batch_size)

    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        c, _ = m1.train(batch_xs, batch_ys)
        avg_cost += c / total_batch
        if i % 10 == 0:
            print("i=", i, "avg_cost=", avg_cost)

print("학습종료!!!")

# 정확도 측정
print(m1.get_accuracy(mnist.test.images, mnist.test.labels))
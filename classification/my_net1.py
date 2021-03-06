import tensorflow as tf
import os
from classification.base_classifier import BaseClassifier
from utils.TensorflowUtils import variable_on_cpu, variable_with_weight_decay


class MyCifar10Classifier(object):
    def __int__(self):
        return

    def __init__(self, num_classes=21):
        self.num_classes = num_classes
        return

    def inference(self, images):
        with tf.variable_scope('conv1') as scope:
            kernel = variable_with_weight_decay('weights',
                                                shape=[5, 5, 3, 64],
                                                stddev=5e-2,
                                                wd=None)
            conv = tf.nn.conv2d(images, kernel, [1, 1, 1, 1], padding='SAME')
            biases = variable_on_cpu('biases', [64], tf.constant_initializer(0.0))
            pre_activation = tf.nn.bias_add(conv, biases)
            conv1 = tf.nn.relu(pre_activation, name=scope.name)

        # pool1
        pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                               padding='SAME', name='pool1')
        # norm1
        norm1 = tf.nn.lrn(pool1, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75,
                          name='norm1')

        # conv2
        with tf.variable_scope('conv2') as scope:
            kernel = variable_with_weight_decay('weights',
                                                shape=[5, 5, 64, 64],
                                                stddev=5e-2,
                                                wd=None)
            conv = tf.nn.conv2d(norm1, kernel, [1, 1, 1, 1], padding='SAME')
            biases = variable_on_cpu('biases', [64], tf.constant_initializer(0.1))
            pre_activation = tf.nn.bias_add(conv, biases)
            conv2 = tf.nn.relu(pre_activation, name=scope.name)

        # norm2
        norm2 = tf.nn.lrn(conv2, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75,
                          name='norm2')
        # pool2
        pool2 = tf.nn.max_pool(norm2, ksize=[1, 3, 3, 1],
                               strides=[1, 2, 2, 1], padding='SAME', name='pool2')

        # local3
        with tf.variable_scope('local3') as scope:
            # Move everything into depth so we can perform a single matrix multiply.
            reshape = tf.reshape(pool2, [images.get_shape()[0], -1])
            dim = reshape.get_shape()[1].value
            weights = variable_with_weight_decay('weights', shape=[dim, 384],
                                                 stddev=0.04, wd=0.004)
            biases = variable_on_cpu('biases', [384], tf.constant_initializer(0.1))
            local3 = tf.nn.relu(tf.matmul(reshape, weights) + biases, name=scope.name)

        # local4
        with tf.variable_scope('local4') as scope:
            weights = variable_with_weight_decay('weights', shape=[384, 192],
                                                 stddev=0.04, wd=0.004)
            biases = variable_on_cpu('biases', [192], tf.constant_initializer(0.1))
            local4 = tf.nn.relu(tf.matmul(local3, weights) + biases, name=scope.name)

        # linear layer(WX + b),
        # We don't apply softmax here because
        # tf.nn.sparse_softmax_cross_entropy_with_logits accepts the unscaled logits
        # and performs the softmax internally for efficiency.
        with tf.variable_scope('softmax_linear') as scope:
            weights = variable_with_weight_decay('weights', [192, self.num_classes],
                                                 stddev=1 / 192.0, wd=None)
            biases = variable_on_cpu('biases', [self.num_classes],
                                     tf.constant_initializer(0.0))
            softmax_linear = tf.add(tf.matmul(local4, weights), biases, name=scope.name)

        return softmax_linear # do not do soft max here.

    def loss(self, logits, labels):
        """Add L2Loss to all the trainable variables.

        Add summary for "Loss" and "Loss/avg".
        Args:
          logits: Logits from inference().
          labels: Labels from distorted_inputs or inputs(). 1-D tensor
                  of shape [batch_size]

        Returns:
          Loss tensor of type float.
        """
        # Calculate the average cross entropy loss across the batch.
        labels = tf.cast(labels, tf.int64)
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=labels, logits=logits, name='cross_entropy_per_example')
        cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')
        tf.add_to_collection('losses', cross_entropy_mean)

        # The total loss is defined as the cross entropy loss plus all of the weight
        # decay terms (L2 loss).
        return tf.add_n(tf.get_collection('losses'), name='total_loss')



if __name__ == '__main__':
    net = MyCifar10Classifier()
    net.build()

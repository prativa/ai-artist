import tensorflow as tf

"""

"""
def model(images_batch, image_height, image_width, channels, num_classes):

    with tf.name_scope('data'):
        #     x = tf.placeholder(tf.float32, shape=[batch_size_per_gpu, image_height * image_width * channels], name='Input')
        #     y = tf.placeholder(tf.float32, shape=[batch_size_per_gpu, num_classes], name='Output')
        x_image = tf.reshape(images_batch, [-1, image_height, image_width, channels], name='images')

    def variable_with_weight_decay(name, shape, stddev, wd):
        dtype = tf.float32
        var = variable_on_cpu( name, shape, tf.truncated_normal_initializer(stddev=stddev, dtype=dtype))
        if wd is not None:
            weight_decay = tf.multiply(tf.nn.l2_loss(var), wd, name='weight_loss')
            tf.add_to_collection('losses', weight_decay)
        return var

    def variable_on_cpu(name, shape, initializer):
        with tf.device('/cpu:0'):
            dtype = tf.float32
            var = tf.get_variable(name, shape, initializer=initializer, dtype=dtype)
        return var

    with tf.variable_scope('conv1') as scope:
        kernel = variable_with_weight_decay('weights', shape=[5, 5, 3, 64], stddev=5e-2, wd=0.0)
        conv = tf.nn.conv2d(x_image, kernel, [1, 1, 1, 1], padding='SAME')
        biases = variable_on_cpu('biases', [64], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv1 = tf.nn.relu(pre_activation, name=scope.name)
    with tf.device('/cpu:0'):
        tf.summary.histogram('Convolution_layers/conv1', conv1)
        tf.summary.scalar('Convolution_layers/conv1', tf.nn.zero_fraction(conv1))

    norm1 = tf.nn.lrn(conv1, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm1')
    pool1 = tf.nn.max_pool(norm1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool1')

    with tf.variable_scope('conv2') as scope:
        kernel = variable_with_weight_decay('weights', shape=[5, 5, 64, 64], stddev=5e-2, wd=0.0)
        conv = tf.nn.conv2d(tf.nn.dropout(pool1,keep_prob=0.6), kernel, [1, 1, 1, 1], padding='SAME')
        biases = variable_on_cpu('biases', [64], tf.constant_initializer(0.1))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv2 = tf.nn.relu(pre_activation, name=scope.name)
    with tf.device('/cpu:0'):
        tf.summary.histogram('Convolution_layers/conv2', conv2)
        tf.summary.scalar('Convolution_layers/conv2', tf.nn.zero_fraction(conv2))

    norm2 = tf.nn.lrn(conv2, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm2')
    pool2 = tf.nn.max_pool(norm2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool2')

    with tf.variable_scope('conv3') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3, 3, 64, 128], stddev=5e-2, wd=0.0)
        conv = tf.nn.conv2d(tf.nn.dropout(pool2,keep_prob=0.6), kernel, [1, 1, 1, 1], padding='SAME')
        biases = variable_on_cpu('biases', [128], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv3 = tf.nn.relu(pre_activation, name=scope.name)

    with tf.device('/cpu:0'):
        tf.summary.histogram('Convolution_layers/conv3', conv3)
        tf.summary.scalar('Convolution_layers/conv3', tf.nn.zero_fraction(conv3))

    with tf.variable_scope('conv4') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3, 3, 128, 128], stddev=5e-2, wd=0.0)
        conv = tf.nn.conv2d(tf.nn.dropout(conv3,keep_prob=0.6), kernel, [1, 1, 1, 1], padding='SAME')
        biases = variable_on_cpu('biases', [128], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv4 = tf.nn.relu(pre_activation, name=scope.name)

    with tf.device('/cpu:0'):
        tf.summary.histogram('Convolution_layers/conv4', conv4)
        tf.summary.scalar('Convolution_layers/conv4', tf.nn.zero_fraction(conv4))

    with tf.variable_scope('conv5') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3, 3, 128, 128], stddev=5e-2, wd=0.0)
        conv = tf.nn.conv2d(tf.nn.dropout(conv4,keep_prob=0.6), kernel, [1, 1, 1, 1], padding='SAME')
        biases = variable_on_cpu('biases', [128], tf.constant_initializer(0.1))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv5 = tf.nn.relu(pre_activation, name=scope.name)

    with tf.device('/cpu:0'):
        tf.summary.histogram('Convolution_layers/conv5', conv5)
        tf.summary.scalar('Convolution_layers/conv5', tf.nn.zero_fraction(conv5))

    norm3 = tf.nn.lrn(conv5, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm3')
    pool3 = tf.nn.max_pool(norm3, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME', name='pool3')

    with tf.variable_scope('fully_connected1') as scope:
        reshape = tf.layers.flatten(pool3)
        dim = reshape.get_shape()[1].value
        weights = variable_with_weight_decay('weights', shape=[dim, 384], stddev=0.04, wd=0.004)
        biases = variable_on_cpu('biases', [384], tf.constant_initializer(0.1))
        local3 = tf.nn.relu(tf.matmul(reshape, weights) + biases, name=scope.name)

    with tf.device('/cpu:0'):
        tf.summary.histogram('Fully connected layers/fc1', local3)
        tf.summary.scalar('Fully connected layers/fc1', tf.nn.zero_fraction(local3))

    with tf.variable_scope('fully_connected2') as scope:
        weights = variable_with_weight_decay('weights', shape=[384, 192], stddev=0.04, wd=0.004)
        biases = variable_on_cpu('biases', [192], tf.constant_initializer(0.1))
        local4 = tf.nn.relu(tf.matmul(local3, weights) + biases, name=scope.name)

    with tf.device('/cpu:0'):
        tf.summary.histogram('Fully connected layers/fc2', local4)
        tf.summary.scalar('Fully connected layers/fc2', tf.nn.zero_fraction(local4))

    with tf.variable_scope('output') as scope:
        weights = variable_with_weight_decay('weights', [192, num_classes], stddev=1 / 192.0, wd=0.0)
        biases = variable_on_cpu('biases', [num_classes], tf.constant_initializer(0.1))
        logits = tf.add(tf.matmul(tf.nn.dropout(local4,keep_prob=0.6), weights), biases, name=scope.name)

    with tf.device('/cpu:0'):
        tf.summary.histogram('Fully connected layers/output', logits)

    return  logits

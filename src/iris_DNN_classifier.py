# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# This is the complete code for the following blogpost:
# https://developers.googleblog.com/2017/09/introducing-tensorflow-datasets.html
#   (https://goo.gl/Ujm2Ep)

import os

import six.moves.urllib.request as request
import tensorflow as tf

# Check that we have correct TensorFlow version installed
tf_version = tf.__version__
print("TensorFlow version: {}".format(tf_version))
assert "1.4" <= tf_version, "TensorFlow r1.4 or later is needed"



# Windows users: You only need to change PATH, rest is platform independent
PATH = "/tmp/tf_dataset_and_estimator_apis"

# Fetch and store Training and Test dataset files
PATH_DATASET = PATH + os.sep + "dataset"
FILE_TRAIN = PATH_DATASET + os.sep + "iris_training.csv"
FILE_TEST = PATH_DATASET + os.sep + "iris_test.csv"
URL_TRAIN = "http://download.tensorflow.org/data/iris_training.csv"
URL_TEST = "http://download.tensorflow.org/data/iris_test.csv"


def downloadDataset(url, file):
    if not os.path.exists(PATH_DATASET):
        os.makedirs(PATH_DATASET)
    if not os.path.exists(file):
        data = request.urlopen(url).read()
        with open(file, "wb") as f:
            f.write(data)
            f.close()
downloadDataset(URL_TRAIN, FILE_TRAIN)
downloadDataset(URL_TEST, FILE_TEST)

tf.logging.set_verbosity(tf.logging.INFO)

# The CSV features in our training & test data
feature_names = [
    'SepalLength',
    'SepalWidth',
    'PetalLength',
    'PetalWidth']

# Create an input function reading a file using the Dataset API
# Then provide the results to the Estimator API


def my_input_fn(file_path, perform_shuffle=False, repeat_count=1):
    def decode_csv(line):
        parsed_line = tf.decode_csv(line, [[0.], [0.], [0.], [0.], [0]])
        label = parsed_line[-1]  # Last element is the label
        del parsed_line[-1]  # Delete last element
        features = parsed_line  # Everything but last elements are the features
        d = dict(zip(feature_names, features)), label
        return d

    dataset = (tf.data.TextLineDataset(file_path)  # Read text file
               .skip(1)  # Skip header row
               .map(decode_csv))  # Transform each elem by applying decode_csv fn
    if perform_shuffle:
        # Randomizes input using a window of 256 elements (read into memory)
        dataset = dataset.shuffle(buffer_size=256)
    dataset = dataset.repeat(repeat_count)  # Repeats dataset this # times
    dataset = dataset.batch(32)  # Batch size to use
    iterator = dataset.make_one_shot_iterator()
    batch_features, batch_labels = iterator.get_next()
    return batch_features, batch_labels

next_batch = my_input_fn(FILE_TRAIN, True)  # Will return 32 random elements

# Create the feature_columns, which specifies the input to our model
# All our input features are numeric, so use numeric_column for each one
feature_columns = [tf.feature_column.numeric_column(k) for k in feature_names]

# Create a deep neural network regression classifier
# Use the DNNClassifier pre-made estimator
classifier = tf.estimator.DNNClassifier(
    feature_columns=feature_columns,  # The input features to our model
    hidden_units=[10, 10],  # Two layers, each with 10 neurons
    n_classes=3,
    model_dir=PATH)  # Path to where checkpoints etc are stored

# Train our model, use the previously function my_input_fn
# Input to training is a file with training example
# Stop training after 8 iterations of train data (epochs)
classifier.train(
    input_fn=lambda: my_input_fn(FILE_TRAIN, True, 8))

# Evaluate our model using the examples contained in FILE_TEST
# Evaluate accuracy.
accuracy_score = classifier.evaluate(input_fn=lambda: my_input_fn(FILE_TEST, False, 1))["accuracy"]
print("\nTest Accuracy: {0:f}\n".format(accuracy_score))


# labels = my_input_fn(FILE_TEST, False, 1)[-1]
# predictions = list(classifier.predict(input_fn=lambda: my_input_fn(FILE_TEST, False, 1)))
# confusion_matrix = tf.confusion_matrix(labels, predictions)


predictions = list(classifier.predict(input_fn=lambda: my_input_fn(FILE_TEST, False, 1)))
print(
    "Test Samples, Raw Predictions:    {}\n"
    .format(predictions))

# predicted_classes = [p["classes"][0] for p in predictions]
predicted_classes = [p["class_ids"][0] for p in predictions]
print(
    "Test Samples, Class Predictions:    {}\n"
    .format(predicted_classes))

labels = []
for line in open(FILE_TEST):
#     print(line)
    parsed_line = tf.decode_csv(line, [[0.], [0.], [0.], [0.], [0]])
    label = parsed_line[-1]  # Last element is the label
#     print(label)
    labels.append(label)
labels = labels[1:]
print(
    "Test Samples, Truth Labels:    {}\n"
    .format(labels))

# labels = my_input_fn(FILE_TEST, False, 1)
# print(
#     "Test Samples, Truth Labels:    {}\n"
#     .format(labels))


# Confusion Matirx
with tf.Session() as sess:
    confusion_matrix = tf.confusion_matrix(labels, predicted_classes,3)
    confusion_matrix_to_Print = sess.run(confusion_matrix)
# print(first_batch_to_Print)   
# tf.Print(confusion_matrix, [confusion_matrix])
print(confusion_matrix_to_Print.eval()) 

# confusion_matrix = tf.confusion_matrix(labels, predicted_classes,3)
# tf.Print(confusion_matrix, [confusion_matrix])
# for i in range(confusion_matrix.shape[0].value):
#     for j in range(confusion_matrix.shape[1].value):
#         tf.Print(confusion_matrix[i][j])
#     print()
# tf.Print(confusion_matrix)






# # Print out some data using a Session
# next_batch = my_input_fn(FILE_TRAIN, True) # Will return 32 random elements
# with tf.Session() as sess:
#     first_batch = sess.run(next_batch)
# print(first_batch)


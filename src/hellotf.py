# https://mubaris.com/2017-10-21/tensorflow-101

# Import TensorFlow
import tensorflow as tf

# Define Constant
output = tf.constant("Hello, World")

# To print the value of constant you need to start a session.
sess = tf.Session()

# Print
print(sess.run(output))

# Close the session
sess.close()

# coding: utf-8

# # MNIST digits classification with TensorFlow

# <img src="images/mnist_sample.png" style="width:30%">

# In[1]:

import numpy as np
from sklearn.metrics import accuracy_score
from matplotlib import pyplot as plt
get_ipython().magic('matplotlib inline')
import tensorflow as tf
print("We're using TF", tf.__version__)

import sys
sys.path.append("../..")
import grading

import matplotlib_utils
from importlib import reload
reload(matplotlib_utils)

import grading_utils
reload(grading_utils)


# # Fill in your Coursera token and email
# To successfully submit your answers to our grader, please fill in your Coursera submission token and email

# In[2]:

grader = grading.Grader(assignment_key="XtD7ho3TEeiHQBLWejjYAA", 
                        all_parts=["9XaAS", "vmogZ", "RMv95", "i8bgs", "rE763"])


# In[40]:

# token expires every 30 min
COURSERA_TOKEN = "5gcenF31Fk1aPO0p"
COURSERA_EMAIL = "arpit.jain2811@gmail.com"


# # Look at the data
# 
# In this task we have 50000 28x28 images of digits from 0 to 9.
# We will train a classifier on this data.

# In[4]:

import preprocessed_mnist
X_train, y_train, X_val, y_val, X_test, y_test = preprocessed_mnist.load_dataset()


# In[5]:

# X contains rgb values divided by 255
print("X_train [shape %s] sample patch:\n" % (str(X_train.shape)), X_train[1, 15:20, 5:10])
print("A closeup of a sample patch:")
plt.imshow(X_train[1, 15:20, 5:10], cmap="Greys")
plt.show()
print("And the whole sample:")
plt.imshow(X_train[1], cmap="Greys")
plt.show()
print("y_train [shape %s] 10 samples:\n" % (str(y_train.shape)), y_train[:10])


# # Linear model
# 
# Your task is to train a linear classifier $\vec{x} \rightarrow y$ with SGD using TensorFlow.
# 
# You will need to calculate a logit (a linear transformation) $z_k$ for each class: 
# $$z_k = \vec{x} \cdot \vec{w_k} + b_k \quad k = 0..9$$
# 
# And transform logits $z_k$ to valid probabilities $p_k$ with softmax: 
# $$p_k = \frac{e^{z_k}}{\sum_{i=0}^{9}{e^{z_i}}} \quad k = 0..9$$
# 
# We will use a cross-entropy loss to train our multi-class classifier:
# $$\text{cross-entropy}(y, p) = -\sum_{k=0}^{9}{\log(p_k)[y = k]}$$ 
# 
# where 
# $$
# [x]=\begin{cases}
#        1, \quad \text{if $x$ is true} \\
#        0, \quad \text{otherwise}
#     \end{cases}
# $$
# 
# Cross-entropy minimization pushes $p_k$ close to 1 when $y = k$, which is what we want.
# 
# Here's the plan:
# * Flatten the images (28x28 -> 784) with `X_train.reshape((X_train.shape[0], -1))` to simplify our linear model implementation
# * Use a matrix placeholder for flattened `X_train`
# * Convert `y_train` to one-hot encoded vectors that are needed for cross-entropy
# * Use a shared variable `W` for all weights (a column $\vec{w_k}$ per class) and `b` for all biases.
# * Aim for ~0.93 validation accuracy

# In[19]:

X_train_flat = X_train.reshape((X_train.shape[0], -1))
print(X_train_flat.shape)

X_val_flat = X_val.reshape((X_val.shape[0], -1))
print(X_val_flat.shape)


# In[20]:

import keras

y_train_oh = keras.utils.to_categorical(y_train, 10)
y_val_oh = keras.utils.to_categorical(y_val, 10)

print(y_train_oh.shape)
print(y_train_oh[:3], y_train[:3])


# In[21]:

# run this if you remake your graph
tf.reset_default_graph()


# In[22]:

# Model parameters: W and b
W = tf.get_variable(name="weights",shape=[784, 10])
b = tf.get_variable(name="bias", shape=[1, 10])


# In[31]:

# Placeholders for the input data
input_X = tf.placeholder(dtype=tf.float32, shape=[None, 784], name="input_x")
input_y = tf.placeholder(dtype=tf.float32, shape=[None, 10], name="output_y")


# In[35]:

# Compute predictions
logits = tf.matmul(input_X, W) + b
probas = tf.nn.softmax(logits=logits)
classes = tf.arg_max(probas, 1)

# Loss should be a scalar number: average loss over all the objects with tf.reduce_mean().
# Use tf.nn.softmax_cross_entropy_with_logits on top of one-hot encoded input_y and logits.
# It is identical to calculating cross-entropy on top of probas, but is more numerically friendly (read the docs).
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=input_y))

# Use a default tf.train.AdamOptimizer to get an SGD step
step = tf.train.AdamOptimizer().minimize(loss)


# In[48]:

s = tf.InteractiveSession()
s.run(tf.global_variables_initializer())

BATCH_SIZE = 512
EPOCHS = 40

# for logging the progress right here in Jupyter (for those who don't have TensorBoard)
simpleTrainingCurves = matplotlib_utils.SimpleTrainingCurves("cross-entropy", "accuracy")

for epoch in range(EPOCHS):  # we finish an epoch when we've looked at all training samples
    
    batch_losses = []
    for batch_start in range(0, X_train_flat.shape[0], BATCH_SIZE):  # data is already shuffled
        _, batch_loss = s.run([step, loss], {input_X: X_train_flat[batch_start:batch_start+BATCH_SIZE], 
                                             input_y: y_train_oh[batch_start:batch_start+BATCH_SIZE]})
        # collect batch losses, this is almost free as we need a forward pass for backprop anyway
        batch_losses.append(batch_loss)

    train_loss = np.mean(batch_losses)
    val_loss = s.run(loss, {input_X: X_val_flat, input_y: y_val_oh})  # this part is usually small
    train_accuracy = accuracy_score(y_train, s.run(classes, {input_X: X_train_flat}))  # this is slow and usually skipped
    valid_accuracy = accuracy_score(y_val, s.run(classes, {input_X: X_val_flat}))  
    simpleTrainingCurves.add(train_loss, val_loss, train_accuracy, valid_accuracy)


# # Submit a linear model

# In[38]:

## GRADED PART, DO NOT CHANGE!
# Testing shapes 
grader.set_answer("9XaAS", grading_utils.get_tensors_shapes_string([W, b, input_X, input_y, logits, probas, classes]))
# Validation loss
grader.set_answer("vmogZ", s.run(loss, {input_X: X_val_flat, input_y: y_val_oh}))
# Validation accuracy
grader.set_answer("RMv95", accuracy_score(y_val, s.run(classes, {input_X: X_val_flat})))


# In[39]:

# you can make submission with answers so far to check yourself at this stage
grader.submit(COURSERA_EMAIL, COURSERA_TOKEN)


# # Adding more layers

# Let's add a couple of hidden layers and see how that improves our validation accuracy.
# 
# Previously we've coded a dense layer with matrix multiplication by hand. 
# But this is not convinient, you have to create a lot of variables and your code becomes a mess. 
# In TensorFlow there's an easier way to make a dense layer:
# ```python
# hidden1 = tf.layers.dense(inputs, 256, activation=tf.nn.sigmoid)
# ```
# 
# That will create all the necessary variables automatically.
# Here you can also choose an activation function (rememeber that we need it for a hidden layer!).
# 
# Now add 2 hidden layers to the code above and restart training.
# You're aiming for ~0.97 validation accuracy here.

# In[47]:

# you can write the code here to get a new `step` operation and then run cells with training loop above
# name your variables in the same way (e.g. logits, probas, classes, etc) for safety
### YOUR CODE HERE ###
# Compute predictions
hidden1 = tf.layers.dense(inputs=input_X, units=256, activation=tf.nn.sigmoid)
hidden2 = tf.layers.dense(inputs=hidden1, units=256, activation=tf.nn.sigmoid)
logits = tf.layers.dense(inputs=hidden2, units=10, activation=None)
probas = tf.nn.softmax(logits=logits)
classes = tf.arg_max(probas, 1)

# Loss should be a scalar number: average loss over all the objects with tf.reduce_mean().
# Use tf.nn.softmax_cross_entropy_with_logits on top of one-hot encoded input_y and logits.
# It is identical to calculating cross-entropy on top of probas, but is more numerically friendly (read the docs).
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=input_y))

# Use a default tf.train.AdamOptimizer to get an SGD step
step = tf.train.AdamOptimizer().minimize(loss)


# # Submit a 2-layer MLP
# Run these cells after training a 2-layer MLP

# In[49]:

## GRADED PART, DO NOT CHANGE!
# Validation loss for MLP
grader.set_answer("i8bgs", s.run(loss, {input_X: X_val_flat, input_y: y_val_oh}))
# Validation accuracy for MLP
grader.set_answer("rE763", accuracy_score(y_val, s.run(classes, {input_X: X_val_flat})))


# In[50]:

# you can make submission with answers so far to check yourself at this stage
grader.submit(COURSERA_EMAIL, COURSERA_TOKEN)


# In[ ]:




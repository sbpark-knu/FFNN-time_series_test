import tensorflow as tf
import csv
import numpy as np
import DataReconstruct as input
from sklearn.metrics import precision_score, recall_score, f1_score

import MakePlots as mk

### tanh
periodic_path = 'D:/DKE/data/Periodic/효종/주기성_데이터.csv'
non_periodic_path = 'D:/DKE/data/Periodic/효종/비주기성_데이터.csv'

learning_rate = 0.01
training_epoch = 100
batch_size = 200
epoch_step = 5

loss_value_list_train = []
loss_value_list_valid = []

accuracy_value_list = []

# Get data
p_data = input.reader(periodic_path)
np_data = input.reader(non_periodic_path)

# Reconstruct for model
X_training, Y_training, X_validation, Y_validation, X_test, Y_test = input.setData2(p_data, np_data)
print(X_training.shape,", ",X_validation.shape,", ",X_test.shape,", ",Y_training.shape,", ",Y_validation.shape,", ",Y_test.shape)

print('Data constructed!')

with open('./check/Y_test.txt','w') as P_write:
    p_list = [i for i in Y_test]
    for item in p_list:
        P_write.write(str(item)+'\n')
with open('./check/Y_vali.txt','w') as P_write:
    p_list = [i for i in Y_test]
    for item in p_list:
        P_write.write(str(item)+'\n')
"""I/O 정의 
    X: 입력 256
    Y: 출력(레이블 수) 2
"""
X = tf.placeholder(tf.float32, [None, 256])
Y = tf.placeholder(tf.float32, [None, 2])
keep_prob = tf.placeholder(tf.float32)  #0.1, 0.2, 0.3

# input
# W1 = tf.get_variable("W1", shape=[512, 500], initializer=tf.contrib.layers.xavier_initializer())
W1 = tf.Variable(tf.random_normal([256, 200]), name="weight1")
b1 = tf.Variable(tf.random_normal([200]))
L1 = tf.matmul(X, W1) + b1
L1 = tf.nn.dropout(L1, keep_prob[0])

"""hidden Layers
    dropout: 
"""
W2 = tf.Variable(tf.random_normal([200, 200]), name="weight2")
b2 = tf.Variable(tf.random_normal([200]))
L2 = tf.nn.tanh(tf.matmul(L1, W2) + b2)
L2 = tf.nn.dropout(L2, keep_prob[1])

# W3 = tf.Variable(tf.random_normal([300, 300]), name="weight3")
W3 = tf.Variable(tf.random_normal([200, 2]), name="weight3")
b3 = tf.Variable(tf.random_normal([2]))
L3 = tf.nn.tanh(tf.matmul(L2, W3) + b3)
# L3 = tf.nn.dropout(L3, keep_prob[1])
hypothesis = tf.nn.dropout(L3, keep_prob[2])

# W4 = tf.Variable(tf.random_normal([300, 2]), name="weight4")
# b4 = tf.Variable(tf.random_normal([2]))
# L4 = tf.nn.tanh(tf.matmul(L3, W4) + b4)
# hypothesis = tf.nn.dropout(L4, keep_prob[2])

p = tf.nn.softmax(hypothesis)

# paramenter
param_list = [W1, W2, W3, b1, b2, b3]

saver = tf.train.Saver(param_list)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=hypothesis, labels=Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# define validation function
h_predict = tf.argmax(p, 1)
correct_y = tf.argmax(Y, 1)
correct_prediction = tf.equal(tf.argmax(p, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

"""Initialize"""
sess = tf.Session()
sess.run(tf.global_variables_initializer())

for epoch in range(training_epoch):
    #Batch processing
    avg_loss = 0.0
    acc = 0.0
    total_batch = int(X_training.__len__() / batch_size)
    for i in range(total_batch):
        batch_xs = X_training[i*batch_size:(i+1)*batch_size]
        batch_ys = Y_training[i*batch_size:(i+1)*batch_size]
        """ Training """
        feed_dict = {X: batch_xs, Y: batch_ys, keep_prob: [1.0, 1.0, 1.0]}
        # feed_dict = {X: batch_xs, Y: batch_ys, keep_prob: [0.9, 0.9, 0.9]}
        _, c = sess.run([optimizer, cost], feed_dict=feed_dict)
        avg_loss += c / total_batch
        # print('Batch: ', (i+1), ', cost: ', c)
        # print('----------------------------------')
    if epoch % epoch_step == 0:
        print("Epoch:", '%04d' % (epoch+1), "cost={:.9f}".format(avg_loss))

    # 매 에폭마다 loss 기록
    loss_value_list_train.append(avg_loss)      # show the result (Training)

    """ Validation """
    if (epoch % 1 == 0) :
        loss_val, acc_val, v_Y, v_p = sess.run([cost, accuracy, correct_y, h_predict], feed_dict={X: X_validation, Y: Y_validation, keep_prob: [1.0, 1.0, 1.0]})
        # print(v_Y[:30])
        # print(v_p[:30])
        print('-- validation -- Epoch: %d, Loss: %f, Accuracy: %f'%(epoch, loss_val, acc_val))
        loss_value_list_valid.append(loss_val)      # show the result (Validation)
        accuracy_value_list.append(acc_val)
        # print('-- validation -- Epoch: %d, Loss: %f, Accuracy: %f'%(epoch, loss_val, acc_val))

print("learning finished!")

save_path = saver.save(sess, "./save/mytest.ckpt")

# Test model
correct_prediction = tf.equal(tf.argmax(p, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
a, p, t_loss, t_Y, t_trained =sess.run([accuracy, p, cost, correct_y, h_predict], feed_dict={X: X_test, Y: Y_test, keep_prob: [1.0, 1.0, 1.0]})

print('Accuracy:', a)
print(p)
print(t_loss)
print('Precision: ', precision_score(t_Y, t_trained))
print('Recall: ', recall_score(t_Y, t_trained))
print('F1 score: ', f1_score(t_Y, t_trained))

######## 저장할 리스트1!

print('save_path', save_path)


with open('./check/Y_label.txt','w') as Y_write:
    y_list = [i for i in t_Y]
    for item in y_list:
        Y_write.write(str(item)+'\n')
with open('./P_label.txt','w') as P_write:
    p_list = [i for i in t_trained]
    for item in p_list:
        P_write.write(str(item)+'\n')
"""
r = random.randint(0, X_data.__len__() - 1)
print('random idx: ',r)
print('Now classification!!', sess.run(tf.argmax(hypothesis, 1), feed_dict={X: X_data[r:r+1], keep_prob: [1.0, 1.0, 1.0]}))
"""
sess.close()
# mk._draw_graph(loss_value_list_valid, accuracy_value_list)
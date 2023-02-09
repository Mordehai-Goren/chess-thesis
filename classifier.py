import os

os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
# from sklearn.metrics.classification import confusion_matrix
import sklearn.svm
# import random
import tensorflow as tf
import time
from sklearn.naive_bayes import GaussianNB

RF_ESTIMATORS = 10

def classify(framework, X, Y, outputs = 2):
    
    if framework=='stockfish':
        return None
    
    if framework=='rnn':
        '''
        model = tf.keras.models.Sequential([
            tf.keras.layers.Embedding(input_dim=1000, output_dim=64),
            
            tf.keras.layers.GRU(256, return_sequences=True),
            tf.keras.layers.SimpleRNN(128),
            
            tf.keras.layers.Dense(outputs)
        ])
        '''

        model = tf.keras.models.Sequential([
            tf.keras.layers.Embedding(input_dim=50, output_dim=16),
            tf.keras.layers.LSTM(32),
            
#             tf.keras.layers.Embedding(input_dim=1000, output_dim=64),
#             tf.keras.layers.LSTM(128),
            
            tf.keras.layers.Dense(outputs)
        ])
        
        '''
        Didn't work:
        model = tf.keras.models.Sequential([
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=True), input_shape=(5, 10)),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),

            tf.keras.layers.Dense(outputs)
        ])
        '''
        
        
        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        
        model.compile(optimizer='adam',
                      loss=loss_fn,
                      metrics=['accuracy'])
        model.fit(X, Y, epochs=3, verbose=True)
        
        return model
    
    if framework=='ann':
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
#             tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(outputs)
        ])
        
        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        
        model.compile(optimizer='adam',
                      loss=loss_fn,
                      metrics=['accuracy'])
        model.fit(X, Y, epochs=3, verbose=False)
#         model.fit(X, Y, epochs=5, verbose=True)
#         model.fit(X, Y, epochs=15, verbose=True)
        return model
    
#     if framework=='lstm':
#         model = tf.keras.models.Sequential([
#             tf.keras.layers.Embedding(input_dim=1000, output_dim=64),
#             
# #             tf.keras.layers.Dense(512, activation='relu'),
#             tf.keras.layers.Dropout(0.2),
#             tf.keras.layers.Dense(outputs)
#         ])
#         
#         loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
#         
#         model.compile(optimizer='adam',
#                       loss=loss_fn,
#                       metrics=['accuracy'])
#         model.fit(X, Y, epochs=3, verbose=False)
# #         model.fit(X, Y, epochs=5, verbose=True)
# #         model.fit(X, Y, epochs=15, verbose=True)
#         return model
    
    
#     model = keras.Sequential()
# # Add an Embedding layer expecting input vocab of size 1000, and
# # output embedding dimension of size 64.
# model.add(layers.Embedding(input_dim=1000, output_dim=64))
# 
# # Add a LSTM layer with 128 internal units.
# model.add(layers.LSTM(128))
# 
# # Add a Dense layer with 10 units.
# model.add(layers.Dense(10))
# 
# model.summary()
    
    if framework=='rf':
        clf = RandomForestClassifier(n_estimators=RF_ESTIMATORS)
#         clf = RandomForestClassifier(n_estimators=100)
        
    if framework=='svm':
#         clf = sklearn.svm.SVC(gamma = 0.0001, C=100)
#         clf = sklearn.svm.SVC(gamma = 0.0001, C=10)
        clf = sklearn.svm.SVC()
        
    if framework=='nb':
        clf = GaussianNB()
        
    if framework in ('rf', 'svm', 'nb'):
        clf.fit(X, Y)
        return clf

def dummyStockfishClassifier(X, Y):
    correct = 0
    all = 0
    for x, y in zip(X, Y):
        if y and x[-1]>0:
            correct+=1
        if not y and x[-1]<=0:
            correct+=1
        
        all+=1
    return correct/all

def evaluate(framework, model, X, Y):
    if framework=='stockfish':
        return dummyStockfishClassifier(X, Y)
    
    if framework=='ann':
        print (model.evaluate(X,  Y, verbose=False)[1])
        return model.evaluate(X,  Y, verbose=False)[1]
    
    if framework=='rnn':
        return model.evaluate(X,  Y, verbose=True)[1]
    
    if framework in ('rf', 'svm', 'nb'):
        pred = model.predict(X)
        return accuracy_score(Y, pred)

if __name__=='__main__':
    pass
from __future__ import print_function
import getpass, os
import numpy as np
import collections
import tensorflow as tf
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM, Input, Bidirectional
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.metrics import categorical_accuracy

###Make it such that the punctuation gets split from the word
#Source: https://medium.com/@david.campion/text-generation-using-bidirectional-lstm-and-doc2vec-models-1-3-8979eb65cb3a

def bidirectional_lstm_model(seq_length, vocab_size):
    print('Building LSTM model.')
    model = Sequential()
    model.add(Bidirectional(LSTM(rnn_size, activation="relu"),input_shape=(seq_length, vocab_size)))
    model.add(Dropout(0.3))
    model.add(Dense(vocab_size))
    model.add(Activation('softmax'))
    
    optimizer = Adam(lr=learning_rate)
    callbacks=[EarlyStopping(patience=2, monitor='val_loss')]
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=[categorical_accuracy])
    print("Model Built!")
    return model

'''
Create a folder to hold an author's works
'''
def create_folder(path):
    try:
        os.makedirs(path) #Attempt to create the directory
    except OSError:       #If the directory already exists the system will throw an error
        pass              #We respond to the system's throw by telling it to do nothing

#Grab a list of folders who represent authors and the contents represent their works
#authors = [f.path for f in os.scandir() if f.is_dir()]
###DEBUGGING: Check the author's are being found
###print(authors)

#Change the operating folder to BASEPATH
##Need to implement a way to choose an author
#os.chdir(authors[0])
#author = authors[0].split("\\")[1]
author = "Nietzsche"
save_dir = r"\Models"
create_folder(save_dir)
#Grab all the text files in the author's folder
works = [i for i in os.listdir() if ".txt" in i] #Grab the text file(s)
#Create an empty string to hold all the contents
culmination = ""
#Grab the contents of each work and append them to the string
for work in works:
    culmination += open(work, 'r',encoding='utf-8').read().lower().replace('‘','\"').replace('’','\"')
    ###DEBUGGING: Check that contents are in fact being read in and appended
    ###print(len(culmination))

#Throw the words into a list
word_list = [word for word in culmination.split()]
#Grab a dictionary where the key is the word and the value is the number of occurrences
word_freq = collections.Counter(word_list)

#Create a mapping from words to int
vocab_inv = {x[0] for x in word_freq.most_common()}
vocab_inv = list(sorted(vocab_inv))

#Map the word to the index
vocab = {x: i for i, x in enumerate(vocab_inv)}
words = [x[0] for x in word_freq.most_common()]
###print(words)
###print(vocab)

print("Vocab Size:",len(words))
print("Unique Words:",len(words2int))

#Change this value to alter how many words to predict
seq_length = 1

sequences = []
next_words = []
for i in range(0, len(word_list) - seq_length):
    sequences.append(word_list[i:i+seq_length])
    next_words.append(word_list[i+seq_length])
print('Num of Sequences:',len(sequences))

vocab_size = len(words)

X = np.zeros((len(sequences), seq_length, vocab_size), dtype=np.bool)
y = np.zeros((len(sequences), vocab_size), dtype=np.bool)
for i, sentence in enumerate(sequences):
    for t, word in enumerate(sentence):
        X[i, t, vocab[word]] = 1
    y[i, vocab[next_words[i]]] = 1

rnn_size = 500 # size of RNN
learning_rate = 0.001 #learning rate
md = bidirectional_lstm_model(seq_length, vocab_size)
md.summary()
batch_size = 32 # minibatch size
num_epochs = 30 # number of epochs

callbacks=[EarlyStopping(patience=4, monitor='val_loss'), ModelCheckpoint(filepath=save_dir + '\\{}'.format(author) + '.{epoch:02d}-{val_loss:.2f}.hdf5',\
                           monitor='val_loss', verbose=0, mode='auto', period=2)]

with tf.device('gpu'):
	#fit the model
	history = md.fit(X, y,
         	        batch_size=batch_size,
                	shuffle=True,
                 	epochs=num_epochs,
                 	callbacks=callbacks,
                 	validation_split=0.1)

#save the model
md.save(save_dir + "/" + '{}-word_based_sentences.h5'.format(author))

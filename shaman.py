'''
@author: Tyler Huffman
@date: November 23, 2019
@description: The RNN model that takes an author's work in, learns, and then generates
@TODO: Account for non-english chars. More philosophers then Nietzsche include quotes in other languages so I have to decide
       to either remove them or include them
'''
#Source: www.tensorflow.org/tutorials/text/text_generation
#Source: https://machinelearningmastery.com/text-generation-lstm-recurrent-neural-networks-python-keras/

from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
import numpy as np
import os, time, sys
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
  model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim,
                              batch_input_shape=[batch_size, None]),
    tf.keras.layers.GRU(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
    tf.keras.layers.Dense(vocab_size)
  ])
  return model


@tf.function
def train_step(inp, target):
  with tf.GradientTape() as tape:
    predictions = model(inp)
    loss = tf.reduce_mean(
        tf.keras.losses.sparse_categorical_crossentropy(
            target, predictions, from_logits=True))
  grads = tape.gradient(loss, model.trainable_variables)
  optimizer.apply_gradients(zip(grads, model.trainable_variables))

  return loss

def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

def generate_text(model, start_string):
  # Evaluation step (generating text using the learned model)

  # Number of characters to generate
  num_generate = 1000

  # Converting our start string to numbers (vectorizing)
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty string to store our results
  text_generated = []

  # Low temperatures results in more predictable text.
  # Higher temperatures results in more surprising text.
  # Experiment to find the best setting.
  temperature = 1.0

  # Here batch size == 1
  model.reset_states()
  for i in range(num_generate):
      predictions = model(input_eval)
      # remove the batch dimension
      predictions = tf.squeeze(predictions, 0)

      # using a categorical distribution to predict the word returned by the model
      predictions = predictions / temperature
      predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      # We pass the predicted word as the next input to the model
      # along with the previous hidden state
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])

  return (start_string + ''.join(text_generated))

def train_on(philosopher):
  try:
    path_to_phil = "Works\\{}\\".format(philosopher)         #Define where to grab the text files
    works = os.listdir(path_to_phil)                         #Grab the name of the text file(s)
  except FileNotFoundError:                                  #Catch the case where the program is fed an invalid path
    print("Error: {} is not a valid directory")              #Inform the user of the error and exit the programs
    sys.exit(0)
  
  text = open(path_to_file, 'rb', encoding='utf-8').read().lower()    #Open the text files, read the contents, and force them into lowercase
  vocab = sorted(set(text))                                   #Grab the number of unique characters

  print("Length of text: {} characters".format(len(text)))
  print("{} unique characters".format(len(vocab)))

  char2idx = {u:i for i, u in enumerate(vocab)}              #Create a map from unique characters to indices
  idx2char = np.array(vocab)                                 #Create a map from integers to unique chars
  text_as_int = np.array([char2idx[c] for c in text])

  print('{')
  for char,_ in zip(char2idx, range(20)):
      print('  {:4s}: {:3d},'.format(repr(char), char2idx[char]))
  print('  ...\n}')

  seq_length = 100
  examples_per_epoch = len(text)//(seq_length+1)

  char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)

  for i in char_dataset.take(5):
      print(idx2char[i.numpy()])

  sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

  for item in sequences.take(5):
      print(repr(''.join(idx2char[item.numpy()])))

  dataset = sequences.map(split_input_target)

  BATCH_SIZE = 64
  BUFFER_SIZE = 10000

  dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

  # Length of the vocabulary in chars
  vocab_size = len(vocab)

  # The embedding dimension
  embedding_dim = 256

  # Number of RNN units
  rnn_units = 1024

  model = Sequential()
  model.add(LTSM(256,input_shape=()))
  model = build_model(
    vocab_size = len(vocab),
    embedding_dim=embedding_dim,
    rnn_units=rnn_units,
    batch_size=BATCH_SIZE)

  optimizer = tf.keras.optimizers.Adam()

  for input_example_batch, target_example_batch in dataset.take(1):
      example_batch_predictions = model(input_example_batch)
      print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

  model.summary()

  example_batch_loss  = loss(target_example_batch, example_batch_predictions)
  print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
  print("scalar_loss:      ", example_batch_loss.numpy().mean())

  ##model.compile(optimizer='adam', loss=loss)

  checkpoint_dir = './training_checkpoints/{}'.format(philosopher)  #Directory where the checkpoints will be saved
  checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")  #Name of the checkpoint files

  checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
      filepath=checkpoint_prefix,
      save_weights_only=True)

  EPOCHS = 10
  for epoch in range(EPOCHS):
    start = time.time()

    # initializing the hidden state at the start of every epoch
    # initally hidden is None
    hidden = model.reset_states()

    for (batch_n, (inp, target)) in enumerate(dataset):
      loss = train_step(inp, target)

      if batch_n % 100 == 0:
        template = 'Epoch {} Batch {} Loss {}'
        print(template.format(epoch+1, batch_n, loss))

    # saving (checkpoint) the model every 5 epochs
    if (epoch + 1) % 5 == 0:
      model.save_weights(checkpoint_prefix.format(epoch=epoch))

    print ('Epoch {} Loss {:.4f}'.format(epoch+1, loss))
    print ('Time taken for 1 epoch {} sec\n'.format(time.time() - start))

  model.save_weights(checkpoint_prefix.format(epoch=epoch))

  ##history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])

  ##tf.train.latest_checkpoint(checkpoint_dir)
  ##model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)

  ##model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

  ##model.build(tf.TensorShape([1, None]))
  model.summary()

  print(generate_text(model, start_string=u"Life,  "))
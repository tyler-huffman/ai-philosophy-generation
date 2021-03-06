'''
@author: Tyler Huffman
@date: November 23, 2019
@description: The RNN model that takes an author's work in, learns, and then generates text character by character
@TODO: Account for non-english chars. More philosophers then Nietzsche include quotes in other languages so I have to figure out how
       to handle them. If more then one text files exists merge them and ignore all files not ending in ".txt". Switch RNN to grab words 
       and learn by predicting the next word, enable loading of pre-trained weights, and add dropout.
'''
#Source: www.tensorflow.org/tutorials/text/text_generation

from __future__ import absolute_import, division, print_function, unicode_literals
from tensorflow import keras
import tensorflow as tf
import numpy as np
import os, time, sys

def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
  model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, batch_input_shape=[batch_size, None]),
    tf.keras.layers.LSTM(rnn_units, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'),
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

def generate_text(model, start_string):
  # Evaluation step (generating text using the learned model)

  # Number of characters to generate
  num_generate = 1000

  # Converting our start string to numbers (vectorizing)
  input_eval = [char2idx[s] for s in start_string.lower()]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty string to store our results
  text_generated = []

  # Low temperatures results in more predictable text.
  # Higher temperatures results in more surprising text.
  # Experiment to find the best setting.
  temperature = 1.3

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

philosopher = "Nietzsche"
try:
  path_to_phil = "Works\\{}\\".format(philosopher)              #Define where to grab the text files
  works = [i for i in os.listdir(path_to_phil) if ".txt" in i] #Grab the text file(s)
except FileNotFoundError:                                  #Catch the case where the program is fed an invalid path
  print("Error: \"{}\" is not a valid directory".format(path_to_phil))   #Inform the user of the error and exit the programs
  sys.exit(0)

compiled_work = ""
for i in range(len(works)):
  path_to_file = path_to_phil + "\\" + works[i]
  text = open(path_to_file, 'r', encoding='utf-8').read().lower()    #Open the text files, read the contents, and force them into lowercase
  compiled_work += text + " "

chars = sorted(list(set(compiled_work)))                                    #Grab the number of unique characters

print("Length of Text: {} characters".format(len(compiled_work)))
print("{} unique characters".format(len(chars)))

char2idx = {u:i for i, u in enumerate(chars)}              #Create a map from unique characters to indices
idx2char = np.array(chars)                                 #Create a map from integers to unique chars
text_as_int = np.array([char2idx[c] for c in compiled_work])

print('{')
for char,_ in zip(char2idx, range(20)):
    print('  {:4s}: {:3d},'.format(repr(char), char2idx[char]))
print('  ...\n}')

seq_length = 100
examples_per_epoch = len(compiled_work)//(seq_length+1)

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
vocab_size = len(chars)

# The embedding dimension
embedding_dim = 256

# Number of RNN units
rnn_units = 1024

#model = tf.keras.models.load_model('\\training_checkpoints\\ckpt_40.data-00000-of-00001')

model = build_model(
  vocab_size = len(chars),
  embedding_dim=embedding_dim,
  rnn_units=rnn_units,
  batch_size=BATCH_SIZE)
'''
for input_example_batch, target_example_batch in dataset.take(1):
    example_batch_predictions = model(input_example_batch)
    print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

model.summary()

example_batch_loss = loss(target_example_batch, example_batch_predictions)
print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
print("scalar_loss:      ", example_batch_loss.numpy().mean())

model.compile(optimizer='adam', loss=loss)
'''
checkpoint_dir = './training_checkpoints/{}'.format(philosopher)  #Directory where the checkpoints will be saved
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")  #Name of the checkpoint files

checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)

EPOCHS = 40

#history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])

#tf.train.latest_checkpoint(checkpoint_dir) #Train the RNN

model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)

model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))
model.build(tf.TensorShape([1, None]))
model.summary()

#Save the entire model
model.save("\\training_checkpoints\\Nietzsche\\Nietzsche.h5")

print(generate_text(model, start_string=u"life,  "))

#generate_text("training_checkpoints\ckpt_10.data-00000-of-00001","Life is ")
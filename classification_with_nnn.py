# -*- coding: utf-8 -*-
"""classification with nnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RX2woiI0dVFYpIwF8F-1W4lF9_PktHBd
"""

pip install -q tensorflow tensorflow-datasets

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow import keras

"""datasets"""

tfds.list_builders()

builder = tfds.builder("rock_paper_scissors")
info = builder.info

info

"""prep"""

ds_train = tfds.load("rock_paper_scissors",split="train")
ds_test = tfds.load("rock_paper_scissors",split="test")

show = tfds.show_examples(info, ds_train)

"""load data as numpy and use one channel cuz u need edges to classify images ,
red = (:,:,0) fr example
"""

train_images = np.array([example["image"].numpy()[:,:,0] for example in ds_train])
train_lables = np.array([example["label"].numpy() for example in ds_train])

test_images = np.array([example["image"].numpy()[:,:,0] for example in ds_test])
test_lables = np.array([example["label"].numpy() for example in ds_test])

type(train_images[0])
train_images.shape
test_images.shape

"""reshape to gray scale"""

train_images = train_images.reshape(2520,300,300,1)
test_images = test_images.reshape(372,300,300,1)

"""rescale from 0-1"""

train_images = train_images.astype("float32")
test_images = test_images.astype("float32")

train_images /= 255
test_images /=255

"""train network - basic NN"""

model = keras.Sequential(
    [
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation="relu"),
     keras.layers.Dense(256, activation="relu"),
     keras.layers.Dense(3,activation="softmax")
    ]
)

model.compile(
    optimizer="adam",
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"]
)
model.fit(train_images,train_lables,epochs=5,batch_size=32)

model.evaluate(test_images, test_lables)

"""train model - CNN (general parameters with 3*3 grid)

basic is over fit cuz it picks alot unneccesary details
"""

model = keras.Sequential(
    [
        keras.layers.Conv2D(64,3,activation="relu",input_shape=(300,300,1)),
     keras.layers.Conv2D(32,3,activation="relu"),
     keras.layers.Flatten(),
     keras.layers.Dense(3,activation="softmax"),

    ]
)
model.compile(
    optimizer="adam",
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"]
)
model.fit(train_images,train_lables,epochs=5,batch_size=32)

model.evaluate(test_images, test_lables)

"""still over fitting lets try anothor approach"""

model = keras.Sequential(
    [
        keras.layers.AveragePooling2D(6,3,input_shape=(300,300,1)),
        keras.layers.Conv2D(64,3,activation="relu"),
     keras.layers.Conv2D(32,3,activation="relu"),
     keras.layers.MaxPool2D(2,2),
     keras.layers.Dropout(0.5),
     keras.layers.Flatten(),
     keras.layers.Dense(128,activation="relu"),
     keras.layers.Dense(3,activation="softmax"),

    ]
)
model.compile(
    optimizer="adam",
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"]
)
model.fit(train_images,train_lables,epochs=5,batch_size=32)

model.evaluate(test_images, test_lables)

"""tuning data

"""

pip install -U keras_tuner

from kerastuner.tuners import RandomSearch

def build_model(hp):
  model = keras.Sequential()

  model.add( keras.layers.AveragePooling2D(6,3,input_shape=(300,300,1)))

  model.add( keras.layers.Conv2D(64,3,activation="relu"))
  model.add( keras.layers.Conv2D(32,3,activation="relu"))

  model.add(keras.layers.MaxPool2D(2,2))
  model.add(keras.layers.Dropout(0.5))
  model.add(  keras.layers.Flatten())

  model.add(keras.layers.Dense(hp.Choice("Dense layer",[62,128,256,512,102]),activation="relu"))

  model.add(keras.layers.Dense(3,activation="softmax"))

  model.compile(
      optimizer="adam",
      loss=keras.losses.SparseCategoricalCrossentropy(),
      metrics=["accuracy"]
  )

  return model

tuner = RandomSearch(
    build_model,
    objective='val_loss',
    max_trials=32,
    )

tuner.search(train_images,train_lables,validation_data=(test_images,test_lables),epochs=5,batch_size=32)

best_model = tuner.get_best_models()[0]

best_model.evaluate(test_images,test_lables)

best_model.summary()

"""adding more layers and filters"""

def build_model(hp):
  model = keras.Sequential()

  model.add( keras.layers.AveragePooling2D(6,3,input_shape=(300,300,1)))

  for i in range(hp.Int("Conv Layers", min_value=0, max_value=3)):
    model.add( keras.layers.Conv2D(hp.Choice(f"layer_{i}_filters",[16,32,64]),3,activation="relu"))


  model.add(keras.layers.MaxPool2D(2,2))
  model.add(keras.layers.Dropout(0.5))
  model.add(  keras.layers.Flatten())

  model.add(keras.layers.Dense(hp.Choice("Dense layer",[62,128,256,512,102]),activation="relu"))

  model.add(keras.layers.Dense(3,activation="softmax"))

  model.compile(
      optimizer="adam",
      loss=keras.losses.SparseCategoricalCrossentropy(),
      metrics=["accuracy"]
  )

  return model

tuner = RandomSearch(
    build_model,
    objective='val_loss',
    max_trials=32,
    directory="./using_tunner_wiz_more_than_filter"
    )

tuner.search(train_images,train_lables,validation_data=(test_images,test_lables),epochs=5,batch_size=32)

best_model = tuner.get_best_models()[0]

best_model.evaluate(test_images,test_lables)

best_model.save("./best_model")

loaded_model = keras.models.load_model("./best_model")

loaded_model.evaluate(test_images,test_lables)

"""plot images from numpy array"""

image = train_images[0].reshape(300,300)
plt.imshow(image)
plt.imshow(image,cmap="Greys_r")

"""plot in rgb scal"""

rgb_images = np.array([example["image"].numpy() for example in ds_train.take(1)])
rgb_image = rgb_images[0]

plt.imshow(rgb_image)
rgb_image.shape

"""read image from internet to numpy"""

import imageio

im = imageio.imread("https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/University_of_Khartoum_001.JPG/278px-University_of_Khartoum_001.JPG")

im_np = np.asarray(im)

im_np.shape
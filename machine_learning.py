from util.util_ML import adjust_data, adjust_data_onehot, scale_data_normal, scale_data_uniform
import tensorflow as tf
from tensorflow import keras
import pandas as pd
import matplotlib.pyplot as plt
from util.util import save_fig
import os


def nn(data, file_name=""):
    print("TensorFlow version is ", tf.__version__)
    print("Keras version is ", keras.__version__)
    num_validation_data = 1500
    sequence, label = data
    sequence_train, label_train = sequence[:-num_validation_data], label[:-num_validation_data]
    sequence_valid, label_valid = sequence[len(sequence) - num_validation_data:], label[len(sequence) - num_validation_data:]

    keras.backend.clear_session()
    model = keras.models.Sequential()
    model.add(keras.layers.Flatten(input_shape=sequence[0].shape))
    model.add(keras.layers.Dense(300, activation="sigmoid"))
    model.add(keras.layers.Dense(150, activation="sigmoid"))
    model.add(keras.layers.Dense(50, activation="sigmoid"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    model.compile(loss="binary_crossentropy",
                  optimizer="adam",
                  metrics="accuracy")

    history = model.fit(sequence_train, label_train, epochs=10, batch_size=32, workers=1,
                        validation_data=(sequence_valid, label_valid), shuffle=True)

    pd.DataFrame(history.history).plot(figsize=(8, 5))
    plt.grid(True)
    plt.gca().set_ylim(0, 1)
    save_fig("300_150_50" + file_name)

    print(model.evaluate(sequence, label))
    filepath = os.path.join(os.getcwd(), "models", "model.h5")
    model.save(filepath)


def test(data):
    filepath = os.path.join(os.getcwd(), "models", "model.h5")
    model = keras.models.load_model(filepath)
    print(model.summary)


def calculate(original_data):
    data = adjust_data_onehot(original_data)
    #nn(data, "onehot")
    test(data[0][9001])
    #data = adjust_data(original_data, scale_data_normal)
    #nn(data, "normal")
    #data = adjust_data(original_data, scale_data_uniform)
    #nn(data, "uniform")
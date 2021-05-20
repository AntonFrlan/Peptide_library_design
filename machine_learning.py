from tensorflow import keras
import pandas as pd
import matplotlib.pyplot as plt
from util import save_fig, adjust_data_onehot
import os


def calculate(original_data=None):
    if original_data is not None:
        data = adjust_data_onehot(original_data)
        return neural_network(data, 1500, "onehot")
    else:
        filepath = os.path.join(os.getcwd(), "models", "model.h5")
        return keras.models.load_model(filepath)


def fitness_function(data, model):
    data = [{"sequence": data}]
    data = adjust_data_onehot(data, False)[0]
    data = data.reshape(-1, 1000)
    return model.predict(data)


def neural_network(data, validation_data_len, file_name="", test_model=False):
    sequence, label = data
    sequence_train, label_train = sequence[:-validation_data_len], label[:-validation_data_len]
    sequence_valid, label_valid = sequence[len(sequence) - validation_data_len:], label[len(sequence) - validation_data_len:]

    keras.backend.clear_session()
    model = keras.models.Sequential()
    model.add(keras.layers.InputLayer(input_shape=sequence[0].shape))
    model.add(keras.layers.Dense(300, activation="sigmoid"))
    model.add(keras.layers.Dense(150, activation="sigmoid"))
    model.add(keras.layers.Dense(50, activation="sigmoid"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    model.compile(loss="binary_crossentropy",
                  optimizer="adam",
                  metrics="accuracy")

    history = model.fit(sequence_train, label_train, epochs=10, batch_size=32, workers=1,
                        validation_data=(sequence_valid, label_valid), shuffle=True)
    if test_model:
        test(history.history, file_name)

    filepath = os.path.join(os.getcwd(), "models", "model.h5")
    model.save(filepath)
    return model


def test(train_data, file_name):
    pd.DataFrame(train_data).plot(figsize=(8, 5))
    plt.grid(True)
    plt.gca().set_ylim(0, 1)
    save_fig("300_150_50_1_" + file_name)

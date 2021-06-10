from tensorflow import keras
import pandas as pd
import matplotlib.pyplot as plt
from util import save_fig, adjust_data_onehot
import os


def get_performance(data, data_file):
    peptide_type = data_file.split('.')[0]
    txt_path = os.path.join(os.getcwd(), "models", peptide_type + ".txt")
    try:
        file = open(txt_path, 'r')
        lines = file.readlines()
        file.close()
        performance = {
            "all": 0,
            "train": 0,
            "valid": 0
        }
        for line in lines:
            name, value = line.split(" , ")
            performance[name] = float(value)
    except:
        performance = neural_network(data, data_file)
    return performance


def get_model(peptide_type):
    peptide_type = peptide_type.split('.')[0]
    model_path = os.path.join(os.getcwd(), "models", peptide_type + ".h5")
    return keras.models.load_model(model_path)


def fitness_function(data, model):
    data = [{"sequence": data}]
    data = adjust_data_onehot(data, False)[0]
    data = data.reshape(-1, 1000)
    return model.predict(data)


def neural_network(data, data_file="", validation_data_len=1500):
    peptide_type = data_file.split('.')[0]

    sequence, label = data
    sequence_train, label_train = sequence[:-validation_data_len], label[:-validation_data_len]
    sequence_valid, label_valid = sequence[len(sequence) - validation_data_len:], label[len(sequence) - validation_data_len:]

    keras.backend.clear_session()
    model = keras.models.Sequential()
    model.add(keras.layers.InputLayer(input_shape=sequence[0].shape))
    model.add(keras.layers.Dense(10, activation="sigmoid"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    model.compile(loss="mean_squared_error",
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

    history = model.fit(sequence_train, label_train, epochs=20, batch_size=32, workers=1,
                        validation_data=(sequence_valid, label_valid), shuffle=True)
    pd.DataFrame(history.history).plot(figsize=(8, 5))
    plt.grid(True)
    plt.gca().set_ylim(0, 1)
    save_fig("d_2" + peptide_type)

    filepath = os.path.join(os.getcwd(), "models", peptide_type + ".h5")
    model.save(filepath)

    performance = {
        "all": 1 - model.evaluate(sequence, label)[1],
        "train": 1 - model.evaluate(sequence_train, label_train)[1],
        "valid": 1 - model.evaluate(sequence_valid, label_valid)[1]
    }

    txt_path = os.path.join(os.getcwd(), "models", peptide_type + ".txt")
    file = open(txt_path, 'w')
    lines = ["all , " + str(performance["all"]), "\ntrain , " + str(performance["train"]), "\nvalid , " + str(performance["valid"])]
    for line in lines:
        file.write(line)
    file.close()
    return performance

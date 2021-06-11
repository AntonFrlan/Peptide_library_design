import inquirer
from tensorflow import keras
import pandas as pd
import matplotlib.pyplot as plt
from inquirer import Path
from util import save_fig, get_peptide_activities, adjust_data_onehot, load_data
import os


def get_performance(peptide_type):
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
        return performance
    except FileNotFoundError:
        return None


def get_model(peptide_type):
    model_path = os.path.join(os.getcwd(), "models", peptide_type + ".h5")
    return keras.models.load_model(model_path)


def neural_network(data, peptide_type, validation_data_len=0.1):
    sequence, label = data
    data_len = len(sequence)
    validation_data_len = round(data_len * validation_data_len)
    sequence_train, label_train = sequence[:-validation_data_len], label[:-validation_data_len]
    sequence_valid, label_valid = sequence[data_len - validation_data_len:], label[data_len - validation_data_len:]

    keras.backend.clear_session()
    model = keras.models.Sequential()
    model.add(keras.layers.InputLayer(input_shape=sequence[0].shape))
    model.add(keras.layers.Dense(20, activation="sigmoid"))
    model.add(keras.layers.Dense(10, activation="sigmoid"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))

    model.compile(loss="mean_squared_error",
                  optimizer="adam",
                  metrics=["mean_absolute_error"])

    history = model.fit(sequence_train, label_train, epochs=12, batch_size=32, workers=1,
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
    lines = ["all , " + str(performance["all"]), "\ntrain , " + str(performance["train"]),
             "\nvalid , " + str(performance["valid"])]
    for line in lines:
        file.write(line)
    file.close()


if __name__ == '__main__':
    choices = get_peptide_activities()
    choices.append("Other (you will have to provide a dataset)")
    activity_type = inquirer.list_input(message="Select peptide activity",
                                        choices=choices)

    if activity_type == "Other (you will have to provide a dataset)":
        # LOL dakle ne smijes pogrijesiti prilikom upisivanja patha i imena.
        # Ako pogriješiš ne radiš delete / go back nego terminiras program
        # i pocinjes opet
        questions = [inquirer.Path("data_path",
                                   message="Enter training dataset path",
                                   exists=True,
                                   path_type=Path.FILE),
                     inquirer.Text("model_name", message="Enter new model name")]
        answers = inquirer.prompt(questions)
        neural_network(adjust_data_onehot(load_data(answers["data_path"])),
                       answers["model_name"])

    p = get_performance(activity_type)
    print("MODEL ACCURACY\n_______________")
    if p is not None:
        print(p)

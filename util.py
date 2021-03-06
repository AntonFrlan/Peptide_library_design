import random
import numpy as np
import os
import matplotlib.pyplot as plt
import csv
from constants import PeptideConstants as pc
import glob


def get_peptide_activities():
    files = os.listdir(os.path.join(os.getcwd(), "models"))
    result = []
    for f in files:
        if f.split('.')[1] == 'txt':
            result.append(f.split('.')[0])
    return result


def balance_data(data, generate):
    new_data = []
    size = len(data) - 1
    for i in range(generate):
        point = round(random.random() * size)
        new_data.append(data[point])
    return new_data


def load_data(file_path):
    unbalanced = 0.30
    pos, neg, label = 0, 0, 0
    pos_data = []
    neg_data = []
    new_data = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        data = []
        for row in csv_reader:
            if line_count == 0 or len(row[0]) > 50:
                line_count += 1
                pass
            else:
                data.append({"sequence": row[0], "label": row[1]})
                line_count += 1
                if int(row[1]) == 1:
                    pos += 1
                    pos_data.append(row[0])
                else:
                    neg += 1
                    neg_data.append(row[0])
        print("Positive data :", pos, "\nNegative data: ", neg)
        if pos * unbalanced > neg:
            new_data = balance_data(neg_data, round(pos * unbalanced - neg))
        elif neg * unbalanced > pos:
            label = 1
            new_data = balance_data(pos_data, round(neg * unbalanced - pos))
        for add in new_data:
            data.append({"sequence": add, "label": label})

        random.shuffle(data)
        print(f'Processed {line_count - 1} lines. In data {len(data)}')
    return data


def save_fig(file_name):
    path = os.path.join(os.getcwd(), "images", file_name + ".png")
    plt.tight_layout()
    plt.title(file_name)
    plt.savefig(path, format="png", dpi=300)


def binary_search(arr, low, high, x):
    while low + 1 < high:
        mid = (high + low) // 2
        if arr[mid] > x:
            high = mid
        else:
            low = mid
    return low


def scale_data_uniform(array):
    new_seq = np.zeros(pc.CONST_PEPTIDE_MAX_LENGTH, dtype=float)
    char_to_int = dict((c, i) for i, c in enumerate(pc.CONST_GENES))

    new_seq[0] = [char_to_int[char] for char in array[0]][0]
    for i in range(pc.CONST_PEPTIDE_MAX_LENGTH):
        try:
            new_seq[i] = [char_to_int[char] for char in array[i]][0] + 1  # 0 is label for null
        except:
            break
    for i in range(len(new_seq)):
        new_seq[i] /= float(pc.CONST_GENE_TYPES)
    return new_seq


def scale_data_normal(array):
    new_seq = np.zeros(pc.CONST_PEPTIDE_MAX_LENGTH, dtype=float)
    for i in range(pc.CONST_PEPTIDE_MAX_LENGTH):
        try:
            new_seq[i] = float(ord(array[i]))
        except:
            break
    for i in range(len(new_seq)):
        new_seq[i] /= pc.CONST_PEPTIDE_MAX_VALUE
    return new_seq


def adjust_data(old_data, scale):
    data_seq = np.empty(shape=[len(old_data), pc.CONST_PEPTIDE_MAX_LENGTH], dtype=float)
    data_lab = np.empty(shape=[len(old_data), 1], dtype=float)
    br = -1
    for peptide in old_data:
        br += 1
        data_seq[br] = scale(peptide["sequence"])
        if peptide["label"] == "1":
            data_lab[br] = 1
    return data_seq, data_lab


def adjust_data_onehot(old_data, label=True):
    data_sequence = np.zeros(shape=[len(old_data), 1000], dtype=int)  # why a thousand? magic number?
    data_label = np.zeros(shape=[len(old_data), 1], dtype=int)
    char_to_int = dict((c, i) for i, c in enumerate(pc.CONST_GENES))
    br = -1

    for peptide in range(len(old_data)):
        new_seq = np.zeros([pc.CONST_PEPTIDE_MAX_LENGTH, pc.CONST_GENE_TYPES], dtype=int)
        for i in range(pc.CONST_PEPTIDE_MAX_LENGTH):
            try:
                value = [char_to_int[char] for char in old_data[peptide]["sequence"][i]]
                onehot_encoded = [0 for _ in range(pc.CONST_GENE_TYPES)]
                onehot_encoded[value[0]] = 1
                new_seq[i] = onehot_encoded
            except:
                break
        br += 1
        data_sequence[br] = new_seq.flatten()
        if label and old_data[peptide]["label"] == "1":
            data_label[br] = 1
    return data_sequence, data_label



def mean(array):
    return float(sum(array)) / len(array)


def plot_results():
    folder = 'models/'
    files = glob.glob(folder + '*.txt')
    files = np.asarray(files)

    ds_name = []
    valid = []
    train = []

    for i in range(0, len(files)):
        ds_name.append((files[i].split('\\')[1]).split('.')[0])
        file = open(files[i], 'r')
        lines = file.readlines()
        file.close()

        for line in lines:
            name, value = line.split(" , ")
            if name == 'train':
                train.append(float(value))
            elif name == 'valid':
                valid.append(float(value))

    x = np.arange(len(ds_name))
    width = 0.35

    fig, ax = plt.subplots()
    minor_ticks = np.arange(0, 1, 0.1)
    ax.set_yticks(minor_ticks, minor=True)
    ax.grid(axis='y', which='both', alpha=0.75, zorder=0)
    ax.bar(x - width / 2, train, width, label='train', zorder=3)
    ax.bar(x + width / 2, valid, width, label='valid', zorder=3)

    plt.ylim(bottom=0.75)
    ax.set_ylabel('Accuracy')
   # ax.set_title('Accuracy for every model - train and validation set')
    ax.set_xticks(x)
    ax.set_xticklabels(ds_name)
    ax.legend()
    fig.tight_layout()

    plt.show()

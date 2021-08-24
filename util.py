import random
import numpy as np
import os
import matplotlib.pyplot as plt
import csv
from constants import PeptideConstants as pc


def get_peptide_activities():
    files = os.listdir(os.path.join(os.getcwd(), "models"))
    result = []
    for f in files:
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
    data_seq = np.zeros(shape=[len(old_data), 1000], dtype=int)
    data_lab = np.zeros(shape=[len(old_data), 1], dtype=int)
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
        data_seq[br] = new_seq.flatten()
        if label and old_data[peptide]["label"] == "1":
            data_lab[br] = 1
    return data_seq, data_lab

def two_datasets(old_data, label=True):
    data_seq1 = []
    data_lab1 = []
    data_seq2 = []
    data_lab2 = []
    pos, neg = True, True
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
        if old_data[peptide]["label"] == "1" and pos or old_data[peptide]["label"] != "1" and neg:
            data_seq1.append(new_seq.flatten())
            data_lab1.append(int(old_data[peptide]["label"]))
            if label and old_data[peptide]["label"] == "1":
                pos = not pos
            else:
                neg = not neg
        else:
            data_seq2.append(new_seq.flatten())
            data_lab2.append(int(old_data[peptide]["label"]))
            if label and old_data[peptide]["label"] == "1":
                pos = not pos
            else:
                neg = not neg
    data_seq1 = np.array(data_seq1)
    data_lab1 = np.array(data_lab1)
    data_seq2 = np.array(data_seq2)
    data_lab2 = np.array(data_lab2)
    print(data_seq1.shape, data_lab1.shape, data_seq2.shape, data_lab2.shape)
    return data_seq1, data_lab1, data_seq2, data_lab2


def mean(array):
    return float(sum(array)) / len(array)

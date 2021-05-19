import numpy as np
from const.peptide_const import peptide_const as pc


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
    data_seq = np.empty(shape=[10341, pc.CONST_PEPTIDE_MAX_LENGTH], dtype=float)
    data_lab = np.empty(shape=[10341, 1], dtype=float)
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

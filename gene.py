from random import random


class Peptoid:
    CONST_GENES = "ABC"
    CONST_GENE_TYPES = 20

    def __init__(self, sequence, label):
        self.gene = sequence
        self.label = label
        self.length = len(sequence)

    def ChanceOfMutation(self):
        return random()
from random import random


class Peptoid:


    def __init__(self, sequence, label):
        self.gene = sequence
        self.label = label
        self.length = len(sequence)

    def ChanceOfMutation(self):
        return random()

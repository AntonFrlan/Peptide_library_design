from random import random
import numpy
from util import BinarySearch
import numpy as np


def RouletteWheel(vjerojatnosti):  # pazi da saljes u RouletteWheel sanse odabira
    vjerojatnosti = np.cumsum(vjerojatnosti)
    rng = random()
    spot = BinarySearch(vjerojatnosti, 0, len(vjerojatnosti) - 1, rng)

    if spot < 0:
        raise ValueError('In RouletteWheel BinarySearch return a number lower than 0 => ' + str(spot))
    return spot


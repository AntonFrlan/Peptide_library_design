import numpy as np
from random import random

def BinarySearch(arr, low, high, x):
    # Check base case
    if high >= low:

        mid = (high + low) // 2

        # If element is present at the middle itself
        if arr[mid] == x:
            return mid

        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif arr[mid] > x:
            return BinarySearch(arr, low, mid - 1, x)

        # Else the element can only be present in right subarray
        else:
            return BinarySearch(arr, mid + 1, high, x)

    else:
        # Element is not present in the array
        return -1

def SortByFitness(population, fitness_scores):
    merged_list = list(zip(population, fitness_scores))
    merged_list.sort(key=lambda merged_list_member: merged_list_member[1])

    sorted_population, sorted_fitness_scores = zip(*merged_list)
    sorted_fitness_scores = np.array(sorted_fitness_scores)+1

    sorted_fitness_scores = sorted_fitness_scores / np.sum(sorted_fitness_scores)
    sorted_fitness_scores = np.cumsum(sorted_fitness_scores)

    return (sorted_population, sorted_fitness_scores)


def RouletteWheel(FitnessScore):  # pazi da saljes FitnessScore u RouletteWheel
    FitnessSum = np.sum(FitnessScore)
    vjerojatnosti = FitnessScore / FitnessSum
    vjerojatnosti = np.cumsum(vjerojatnosti)
    rng = random()
    spot = BinarySearch(vjerojatnosti, 0, len(vjerojatnosti) - 1, rng)

    if spot < 0:
        raise ValueError('In RouletteWheel BinarySearch return a number lower than 0 => ' + str(spot))
    return spot
import numpy as np
from random import random
import os
import matplotlib.pyplot as plt

def BinarySearch(arr, low, high, x):
    # Check base case
    while low + 1 < high:
        mid = (high + low) // 2
        if arr[mid] > x:
            high = mid
        else:
            low = mid
    return low

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


def save_fig(fig_id, img_path=os.path.join(os.getcwd(), "images"), tight_layout=True, fig_extension="png", resolution=300):
    path = os.path.join(img_path, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.title(fig_id)
    plt.savefig(path, format=fig_extension, dpi=resolution)

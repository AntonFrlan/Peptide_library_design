import random
import numpy as np
from constants import PeptideConstants as pc
from util import binary_search


class GeneticEvolution:
    def __init__(
            self,
            fitness_function,
            model,
            population_size=1000,
            offspring_size=1000,
            mutation_probability=0.05,
            num_generations=10000
    ):
        self.fitness_function = fitness_function
        self.model = model
        self.population_size = population_size
        self.offspring_size = offspring_size
        self.mutation_probability = mutation_probability
        self.num_generations = num_generations

    def calculate(self):
        population = self.generate_random_population()
        fitness_scores = self.evaluate_population(population)

        max_fitness_list = []
        generation_number = 1

        while self.check_stopping_condition(population) and generation_number <= self.num_generations:
            print('Generation: {}/{}'.format(generation_number, self.num_generations))

            population = self.create_children(population, fitness_scores)

            fitness_scores = self.evaluate_population(population)

            max_fitness_list.append(self.fitness_function(population[-1]))
            # TODO ako se nismo unaprijedili X generacija treba napraviti NeighbourhoodSearch
            # solution = self.NeighbourhoodSearch(population[:20])
            # if solution is not None:
            #     return(solution, self.fitness_function(solution) ,max_fitness_list)
            generation_number += 1

        # Last solution in the list is the one with best fitness score.
        solution = population[-1]
        distance = self.fitness_function(solution)

        return solution, distance, max_fitness_list

    def generate_random_population(self):
        population = []
        fitness_score = np.zeros(pc.CONST_GENE_TYPES) + 1. / pc.CONST_GENE_TYPES
        for i in range(self.population_size):
            gene_size = round(random.random() * pc.CONST_PEPTIDE_MAX_LENGTH)
            gene = ""
            for j in range(gene_size):
                gene += pc.CONST_GENES[roulette_wheel(fitness_score)]
            population.append(gene)
        return population

    def evaluate_population(self, population):
        fitness_scores = []

        for solution in population:
            total_distance = self.fitness_function(solution)
            fitness_scores.append(total_distance)

        return fitness_scores

    def check_stopping_condition(self, population):
        # TODO provjeri cilj
        return True

    def create_children(self, population, fitness_scores):
        # TODO stvori djecu, uzmi top 20% od roditelja a ostalih 80% stvori krizanjem
        return ...

    def selection(self, population, fitness_scores):
        sorted_population, sorted_fitness_scores = sort_by_fitness(population, fitness_scores)

        return list(sorted_population[-self.population_size:])

    def neighbourhood_search(self, population):
        # TODO NeighbourhoodSearch na X najboljih
        return None


def sort_by_fitness(population, fitness_scores):
    merged_list = list(zip(population, fitness_scores))
    merged_list.sort(key=lambda merged_list_member: merged_list_member[1])

    sorted_population, sorted_fitness_scores = zip(*merged_list)
    sorted_fitness_scores = np.array(sorted_fitness_scores)+1

    sorted_fitness_scores = sorted_fitness_scores / np.sum(sorted_fitness_scores)
    sorted_fitness_scores = np.cumsum(sorted_fitness_scores)

    return sorted_population, sorted_fitness_scores


def roulette_wheel(fitness_score):
    fitness_sum = np.sum(fitness_score)
    p = fitness_score / fitness_sum
    p = np.cumsum(p)
    rng = random.random()
    spot = binary_search(p, 0, len(p) - 1, rng)

    if spot < 0:
        raise ValueError('In RouletteWheel BinarySearch return a number lower than 0 => ' + str(spot))
    return spot

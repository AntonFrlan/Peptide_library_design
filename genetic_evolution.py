import random
import numpy as np
from constants import PeptideConstants as pc
from util import binary_search, mean
import multiprocessing as mp


class GeneticEvolution:
    def __init__(
            self,
            fitness_function,
            model,
            population_size=100,
            mutation_probability=0.05,
            num_generations=10000,
            stop=0.95,
            neighbourhood_search_counter=5,
            neighbourhood_search_percentage=0.05,  # amount of population in search
            number_of_islands=5
    ):
        self.fitness_function = fitness_function
        self.model = model
        self.population_size = population_size
        self.mutation_probability = mutation_probability
        self.num_generations = num_generations
        self.stop = stop
        self.neighbourhood_search_counter = neighbourhood_search_counter
        self.neighbourhood_search_percentage = 1 - neighbourhood_search_percentage
        self.number_of_islands = min(number_of_islands, mp.cpu_count())

    def calculate(self):
        population = self.generate_random_population()
        fitness_scores = self.evaluate_population(population)
        population, fitness_scores = sort_by_fitness(population, fitness_scores)
        avg_mean = mean(fitness_scores)
        print(avg_mean)
        neighbourhood_search_counter = 0

        max_fitness_list = []
        generation_number = 1
        print(population[0], population[-1])
        print(self.fitness_function(population[0], self.model), self.fitness_function(population[-1], self.model),
              generation_number)

        while self.check_stopping_condition(fitness_scores[-1]) and generation_number <= self.num_generations:
            print('Generation: {}/{}'.format(generation_number, self.num_generations))
            print("Best: ", population[-1], fitness_scores[-1], len(population))
            print("Search counter: ", neighbourhood_search_counter)

            population = self.create_children(population, fitness_scores)
            fitness_scores = self.evaluate_population(population)
            population, fitness_scores = sort_by_fitness(population, fitness_scores)
            fitness_mean = mean(fitness_scores)
            print(fitness_mean)

            # max_fitness_list.append(fitness_scores)
            if fitness_mean - avg_mean < 0.001:
                neighbourhood_search_counter += 1
                if self.neighbourhood_search_counter < neighbourhood_search_counter:
                    print("USAO SAM")
                    neighbourhood_search_counter = 0
                    solution = self.neighbourhood_search(population[round(self.population_size * self.neighbourhood_search_percentage):])
                    for pop in solution:
                        population.append(pop)
            else:
                neighbourhood_search_counter = 0
            avg_mean = (avg_mean + fitness_mean) / 2
            generation_number += 1

        # Last solution in the list is the one with best fitness score.
        print(population[0], population[-1])
        print(self.fitness_function(population[0], self.model), self.fitness_function(population[-1], self.model),
              generation_number)
        solution = population[-1]
        distance = self.fitness_function(solution, self.model)

        return solution, distance  # , max_fitness_list

    def generate_random_population(self):
        population = []
        fitness_score = np.zeros(pc.CONST_GENE_TYPES) + 1. / pc.CONST_GENE_TYPES
        for i in range(self.population_size):
            new_len = round(random.random() * pc.CONST_PEPTIDE_MAX_LENGTH)
            gene_size = new_len if pc.CONST_PEPTIDE_MIN_LENGTH < new_len else pc.CONST_PEPTIDE_MIN_LENGTH
            gene = ""
            for j in range(gene_size):
                gene += pc.CONST_GENES[roulette_wheel(fitness_score)]
            population.append(gene)
        return population

    def evaluate_population(self, population):
        fitness_scores = []

        for solution in population:
            total_distance = self.fitness_function(solution, self.model)
            fitness_scores.append(total_distance)

        return fitness_scores

    def check_stopping_condition(self, fitness_score):
        if fitness_score >= self.stop:
            return False
        return True

    def create_children(self, population, fitness_scores):
        kids = []
        for i in population[round(self.population_size * 0.8):]:
            kids.append(i)

        while len(kids) < self.population_size:
            parents = []
            parents.append(population[roulette_wheel(fitness_scores)])
            parents.append(population[roulette_wheel(fitness_scores)])
            if parents[0] != parents[1]:
                kid1, kid2 = self.create_siblings(parents)
                kids.append(kid1)
                kids.append(kid2)
        return kids

    def create_siblings(self, parents):
        parent1, parent2 = parents
        len1 = len(parent1)
        len2 = len(parent2)
        while True:
            break_point = random.random()

            point1 = round(len1 * break_point)
            point2 = round(len2 * break_point)

            kid1 = self.mutate(parent1[:point1] + parent2[point2:])
            kid2 = self.mutate(parent2[:point2] + parent1[point1:])
            if 2 <= len(kid1) <= 50 and 2 <= len(kid2) <= 50:
                return kid1, kid2

    def mutate(self, kid):
        if random.random() <= self.mutation_probability:
            point = round(random.random() * len(kid)) - 1
            kid = self.search(kid, point)[0]  # it returns gene and its score
        return kid

    def selection(self, population, fitness_scores):
        sorted_population, sorted_fitness_scores = sort_by_fitness(population, fitness_scores)

        return list(sorted_population[-self.population_size:])

    def search(self, gene, point):
        best = gene
        score = 0
        for i in pc.CONST_GENES:
            if i != gene[point]:
                new_gene = gene[:point] + i + gene[point + 1:] if point + 1 < len(gene) else gene[:point] + i
                new_score = self.fitness_function(gene, self.model)
                if score < new_score:
                    score = new_score
                    best = new_gene
        return best, score

    def neighbourhood_search(self, population):
        new_population = []
        for pop in population:
            new_population.append(self.dfs(pop))
            new_population.append(self.bfs(pop))
        return new_population

    def bfs(self, pop):
        pop_len = len(pop)
        new_pop = pop
        pop_score = 0
        for point in range(pop_len):
            new_gene, new_gene_score = self.search(pop, point)
            # if not self.check_stopping_condition(new_gene_score):
            #     return new_gene
            if pop_score < new_gene_score and pop != new_gene:
                new_pop = new_gene
                pop_score = new_gene_score
        return new_pop

    def dfs(self, pop):
        pop_len = len(pop)
        new_gene = pop
        new_pop = pop
        pop_score = 0
        for point in range(pop_len):
            new_gene, new_gene_score = self.search(new_gene, point)
            # if not self.check_stopping_condition(new_gene_score):
            #     return new_gene
            if pop_score < new_gene_score and pop != new_gene:
                new_pop = new_gene
                pop_score = new_gene_score
        return new_pop, pop_score


def sort_by_fitness(population, fitness_scores):
    merged_list = list(zip(population, fitness_scores))
    merged_list.sort(key=lambda merged_list_member: merged_list_member[1])

    sorted_population, sorted_fitness_scores = zip(*merged_list)
    sorted_fitness_scores = np.array(sorted_fitness_scores)  # + 1

    # sorted_fitness_scores = sorted_fitness_scores / np.sum(sorted_fitness_scores)
    # sorted_fitness_scores = np.cumsum(sorted_fitness_scores)

    return list(sorted_population), sorted_fitness_scores


def roulette_wheel(fitness_score):
    fitness_sum = np.sum(fitness_score)
    p = fitness_score / fitness_sum
    p = np.cumsum(p)
    rng = random.random()
    spot = binary_search(p, 0, len(p) - 1, rng)

    if spot < 0:
        raise ValueError('In RouletteWheel BinarySearch return a number lower than 0 => ' + str(spot))
    return spot

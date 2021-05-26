import random
import numpy as np
from constants import PeptideConstants as pc
from util import binary_search, mean


class GeneticEvolution:
    def __init__(
            self,
            fitness_function,
            model,
            population_size=100,
            mutation_probability=0.05,
            num_generations=10000,
            stop=0.99,
            neighbourhood_search_counter=5
    ):
        self.fitness_function = fitness_function
        self.model = model
        self.population_size = population_size
        self.mutation_probability = mutation_probability
        self.num_generations = num_generations
        self.stop = stop
        self.neighbourhood_search_counter = neighbourhood_search_counter

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
            print("Best: ", population[-1], fitness_scores[-1])

            population = self.create_children(population, fitness_scores)
            fitness_scores = self.evaluate_population(population)
            population, fitness_scores = sort_by_fitness(population, fitness_scores)
            fitness_mean = mean(fitness_scores)
            print(fitness_mean)

            # max_fitness_list.append(fitness_scores)
            if abs(avg_mean - fitness_mean) < 0.00001:
                neighbourhood_search_counter += 1
                if self.neighbourhood_search_counter < neighbourhood_search_counter:
                    neighbourhood_search_counter = 0
                    solution = self.neighbourhood_search(population[round(self.population_size * 0.8):])
                    if solution is not None:
                        return solution, self.fitness_function(solution)  # ,max_fitness_list
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
            for j in range(2):
                parents.append(population[roulette_wheel(fitness_scores)])
            kid1, kid2 = self.create_siblings(parents)
            kids.append(kid1)
            kids.append(kid2)
        return kids

    def create_siblings(self, parents):
        parent1, parent2 = parents
        len1 = len(parent1)
        len2 = len(parent2)
        break_point = random.random()

        point1 = round(len1 * break_point)
        point2 = round(len2 * break_point)

        kid1 = self.mutate(parent1[:point1] + parent2[point2:])
        kid2 = self.mutate(parent2[:point2] + parent1[point1:])
        return kid1, kid2

    def mutate(self, kid):
        if random.random() <= self.mutation_probability:
            point = round(random.random() * len(kid)) - 1
            kid = self.search(kid, point)

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
                    best = new_gene
        return best

    def neighbourhood_search(self, population):
        print("ULAZIM U NEIGHBOURHOOD_SERACH")
        for pop in population:
            neighbour = self.bfs(pop)
            if neighbour is not None:
                return neighbour
        print("NISAM NASAO RJESENJE :,(")
        return None

    def bfs(self, pop):
        pop_len = len(pop)
        for point in range(pop_len):
            for amino in pc.CONST_GENES:
                new_gene = pop[:point] + amino + pop[point + 1:] if point + 1 < pop_len else pop[:point] + amino
                score = self.fitness_function(new_gene, self.model)
                if not self.check_stopping_condition(score):
                    return new_gene
        return None

    def dfs(self, pop):
        pop_len = len(pop)
        pop_score = 0
        for point in range(pop_len):
            for amino in pc.CONST_GENES:
                new_gene = pop[:point] + amino + pop[point + 1:] if point + 1 < pop_len else pop[:point] + amino
                new_gene_score = self.fitness_function(new_gene, self.model)
                if not self.check_stopping_condition(new_gene_score):
                    return new_gene
                if pop_score < new_gene_score:
                    pop = new_gene
        return None


def sort_by_fitness(population, fitness_scores):
    merged_list = list(zip(population, fitness_scores))
    merged_list.sort(key=lambda merged_list_member: merged_list_member[1])

    sorted_population, sorted_fitness_scores = zip(*merged_list)
    sorted_fitness_scores = np.array(sorted_fitness_scores)  # + 1

    # sorted_fitness_scores = sorted_fitness_scores / np.sum(sorted_fitness_scores)
    # sorted_fitness_scores = np.cumsum(sorted_fitness_scores)

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
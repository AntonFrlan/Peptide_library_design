import random
import inquirer
import numpy as np
from constants import PeptideConstants as pc
from machine_learning import get_model
from util import binary_search, mean, adjust_data_onehot, get_peptide_activities
import multiprocessing as mp


class GeneticEvolution:
    def __init__(
            self,
            model,
            population_size=100,
            mutation_probability=0.05,
            num_generations=10000,
            stop=0.95,
            neighbourhood_search_counter=5,
            neighbourhood_search_percentage=0.05,  # amount of population in search
            number_of_islands=5,
            elitism=0.1
    ):
        self.model = model
        self.population_size = population_size
        self.mutation_probability = mutation_probability
        self.num_generations = num_generations
        self.stop = stop
        self.neighbourhood_search_counter = neighbourhood_search_counter
        self.neighbourhood_search_percentage = 1 - neighbourhood_search_percentage
        self.number_of_islands = min(number_of_islands, mp.cpu_count())
        self.elitism = 1 - elitism
        self.calculate()

    def fitness_function(self, peptide):
        peptide = [{"sequence": peptide}]
        peptide = adjust_data_onehot(peptide, False)[0]
        peptide = peptide.reshape(-1, 1000)
        return self.model.predict(peptide)

    def calculate(self):
        population = self.generate_random_population()
        fitness_scores = self.evaluate_population(population)
        population, fitness_scores = sort_by_fitness(population, fitness_scores)
        avg_mean = mean(fitness_scores)
        print(avg_mean)
        neighbourhood_search_counter = 0

        generation_number = 1
        print(population[0], population[-1])
        print(self.fitness_function(population[0]), self.fitness_function(population[-1]),
              generation_number)

        while self.check_stopping_condition(fitness_scores[-1]) and generation_number <= self.num_generations:
            print('Generation: {}/{}'.format(generation_number, self.num_generations))
            print("Best: ", population[-1], fitness_scores[-1], len(population))
            print("Search counter: ", neighbourhood_search_counter)

            population, length = self.create_children(population, fitness_scores)
            fitness_scores = self.evaluate_population(population)
            population, fitness_scores = sort_by_fitness(population, fitness_scores)
            fitness_mean = mean(fitness_scores)
            print("fitness_mean ", fitness_mean)
            print("average length ", sum(length) / self.population_size)

            # max_fitness_list.append(fitness_scores)
            if fitness_mean - avg_mean < 0.001:
                neighbourhood_search_counter += 1
                if self.neighbourhood_search_counter < neighbourhood_search_counter:
                    print("USAO SAM")
                    neighbourhood_search_counter = 0
                    solution = self.neighbourhood_search(population[round(self.population_size * self.neighbourhood_search_percentage):])
                    for pop in solution:
                        population.append(pop)
                    print("IZASAO SAM")
            else:
                neighbourhood_search_counter = 0
            avg_mean = (avg_mean + fitness_mean) / 2
            generation_number += 1
            print()

        index = next(i for i, fs in enumerate(fitness_scores) if fs > 0.93)
        for i in range(index, len(population)):
            print(population[i], fitness_scores[i])
        return population[index:], fitness_scores[index:]

    def generate_random_population(self):
        population = []
        # all aminoacids are equally likely to be chosen
        probabilities = np.zeros(pc.CONST_GENE_TYPES) + 1. / pc.CONST_GENE_TYPES
        while len(population) < self.population_size:
            new_len = round(random.random() * pc.CONST_PEPTIDE_MAX_LENGTH)
            gene_size = new_len if pc.CONST_PEPTIDE_MIN_LENGTH < new_len else pc.CONST_PEPTIDE_MIN_LENGTH
            gene = ""
            for j in range(gene_size):
                gene += pc.CONST_GENES[roulette_wheel(probabilities)]
            if gene not in population:
                population.append(gene)
        return population

    def evaluate_population(self, population):
        fitness_scores = []

        for solution in population:
            total_distance = self.fitness_function(solution)
            fitness_scores.append(total_distance)

        return fitness_scores

    def check_stopping_condition(self, fitness_score):
        if fitness_score >= self.stop:
            return False
        return True

    def create_children(self, population, fitness_scores):
        print("CREATE CHILDREN")
        kids = []
        for i in population[round(self.population_size * self.elitism):]:
            kids.append(i)

        lengths = []
        while len(kids) < self.population_size:
            parent1 = population[roulette_wheel(fitness_scores)]
            parent2 = population[roulette_wheel(fitness_scores)]
            if parent1 == parent2:
                continue
            kid, length = self.create_siblings([parent1, parent2])
            kids.append(kid)
            lengths.append(length)
        print("DONE WITH CHILDREN")
        return list(kids), lengths

    def create_siblings(self, parents):
        parent1, parent2 = parents
        len1 = len(parent1)
        len2 = len(parent2)
        while True:
            break_point1 = random.random()
            break_point2 = random.random()

            point1 = round(len1 * break_point1)
            point2 = round(len2 * break_point2)
            kid = parent1[:point1] + parent2[point2:]
            length = len(kid)
            if 2 <= length <= 50:
                kid = self.mutate(kid)
                return kid, length

    def mutate(self, kid):
        if random.random() <= self.mutation_probability:
            point = round(random.random() * (len(kid) - 1))
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
                new_score = self.fitness_function(gene)
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
        return new_pop


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


if __name__ == '__main__':
    peptide_activity = inquirer.list_input(message="Select peptide activity:",
                                           choices=get_peptide_activities())
    GeneticEvolution(get_model(peptide_activity))

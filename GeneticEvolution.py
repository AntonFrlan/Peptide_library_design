from util import RouletteWheel, SortByFitness


class GemeticEvolution:
    def __init__(
            self,
            fitness_function,
            population_size,
            offspring_size,
            mutation_probability,
            num_generations
    ):
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.offspring_size = offspring_size
        self.mutation_probability = mutation_probability
        self.num_generations = num_generations

    def calculate(self, iterations):
        population = self.GenerateRandomPopulation()
        fitness_scores = self.EvaluatePopulation(population)

        max_fitness_list = []
        GeneratioNumber = 1

        while self.CheckStoppingCondition(population) and GeneratioNumber <= iterations:
            print('Generation: {}/{}'.format(GeneratioNumber, self.num_generations))

            population = self.CreateChildren(population, fitness_scores)

            fitness_scores = self.EvaluatePopulation(population)

            max_fitness_list.append(self.fitness_function(population[-1]))
            # TODO ako se nismo unaprijedili X generacija treba napraviti NeighbourhoodSearch
            # solution = self.NeighbourhoodSearch(population[:20])
            # if solution is not None:
            #     return(solution, self.fitness_function(solution) ,max_fitness_list)
            GeneratioNumber += 1

        # Last solution in the list is the one with best fitness score.
        solution = population[-1]
        distance = self.fitness_function(solution)

        return (solution, distance, max_fitness_list)

    def GenerateRandomPopulation(self):
        # TODO generate population
        return ...

    def EvaluatePopulation(self, population):
        fitness_scores = []

        for solution in population:
            total_distance = self.fitness_function(solution)
            fitness_scores.append(total_distance)

        return fitness_scores

    def CheckStoppingCondition(self, population):
        # TODO provjeri cilj
        return True

    def CreateChildren(self, population, fitness_scores):
        # TODO stvori djecu, uzmi top 20% od roditelja a ostalih 80% stvori krizanjem
        return ...

    def Selection(self, population, fitness_scores):
        sorted_population, sorted_fitness_scores = SortByFitness(population, fitness_scores)

        return list(sorted_population[-self.population_size:])

    def NeighbourhoodSearch(self, population):  # Anton
        # TODO NeighbourhoodSearch na X najboljih
        return None

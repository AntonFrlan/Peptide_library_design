import os
from util import load_data
import machine_learning as ml
from genetic_evolution import GeneticEvolution as ge

if __name__ == '__main__':
    file_path = os.path.join(os.getcwd(), "generated_datasets", "antimicrobial.csv")
    data = load_data(file_path)
    model = ml.calculate(data)
    ge(ml.fitness_function, model).calculate()

import machine_learning as ml
from genetic_evolution import GeneticEvolution as ge
import os
from util import adjust_data_onehot, load_data

if __name__ == '__main__':
    peptide_type = "antigram_minus.csv"  # birati ga s argumentima tokom poziva
    data_path = os.path.join(os.getcwd(), "generated_datasets", peptide_type)
    data = adjust_data_onehot(load_data(data_path))
    print(ml.get_performance(data, peptide_type))
    model = ml.get_model(peptide_type)
    g = ge(ml.fitness_function, model)
    print(g.calculate())

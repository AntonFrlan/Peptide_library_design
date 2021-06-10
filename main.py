import machine_learning as ml
from genetic_evolution import GeneticEvolution as ge

if __name__ == '__main__':
    peptide_type = "antimicrobial.csv"  # birati ga s argumentima tokom poziva
    print(ml.get_performance(peptide_type))
    model = ml.get_model(peptide_type)
    g = ge(ml.fitness_function, model)
    print(g.calculate())

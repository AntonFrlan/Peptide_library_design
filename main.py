import GeneticEvolution
import csv
import os
from const.peptide_const import peptide_const as pc
import machine_learning as ml


def load_data(file):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        data = []
        for row in csv_reader:
            if line_count == 0 or len(row[0]) > 50:
                line_count += 1
                pass
            else:
                data.append({"sequence": row[0], "label": row[1]})
                line_count += 1
        print(f'Processed {line_count - 1} lines. In data {len(data)}')
    return data


def machineLearning(file_path):  # Anton
    ml.calculate(load_data(file_path))


def Petra():  # Petra
    print("TODO")


def geneticEvolution():
    print("TODO")


if __name__ == '__main__':
    print("Peekaboo :D")
    file_path = os.path.join(os.getcwd(), "generated_datasets", "antimicrobial.csv")
    machineLearning(file_path)

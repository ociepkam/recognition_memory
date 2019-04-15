import csv
import yaml
from os.path import join
from numpy.random import shuffle


def load_config():
    try:
        with open(join("config.yaml")) as yaml_file:
            doc = yaml.load(yaml_file)
        return doc
    except:
        raise Exception("Can't load config file")


def prepare_words(file_name, experiment_version):
    try:
        exp_data = []
        train_data = []
        with open(join("stimulus", file_name), 'r') as file:
            data = csv.reader(file)
            for idx, row in enumerate(data):
                if idx != 0:
                    if row[3] == "TREN":
                        train_data.append({'NAWL_NR': row[0], 'WORD': row[1], 'WORD_EMO': row[2], 'WORD_LIST': row[3],
                                           'WORD_TYPE': "TREN"})
                    else:
                        exp_data.append({'NAWL_NR': row[0], 'WORD': row[1], 'WORD_EMO': row[2], 'WORD_LIST': row[3],
                                         'WORD_TYPE': 'exp' if row[3] == experiment_version else "new"})
    except:
        raise Exception("Can't load {} file".format(file_name))

    shuffle(exp_data)
    shuffle(train_data)
    return exp_data, train_data

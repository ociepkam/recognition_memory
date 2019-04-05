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


def load_words(filename):
    try:
        with open(join("stimulus", filename)) as file:
            results = []
            for line in file:
                results.append(line.split("\n")[0])
        return results
    except:
        raise Exception("Can't load {} file".format(filename))


def prepare_words(file_words_exp, file_words_new):
    words_exp = [(word, "exp") for word in load_words(file_words_exp)]
    words_new = [(word, "new") for word in load_words(file_words_new)]
    words_all = words_exp + words_new
    shuffle(words_all)
    return words_all


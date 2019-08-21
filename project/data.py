# Ben-Ryder 2019
# Currently using PICKLE as method of file save

import pickle
import os


def save(game, filename):
    with open(filename, "wb") as file:
        pickle.dump(game, file)


def load(filename):
    with open(filename, "rb") as file:
        game = pickle.load(file)
    return game


def delete(filename):
    os.remove(filename)


def check_exists(filename):
    return os.path.isfile(filename)

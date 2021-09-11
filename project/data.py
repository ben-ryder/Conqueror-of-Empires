# Currently using JSON as method of file save

import json
import os

import constants


def save(data, filename):
    with open(filename + ".json", "w") as file:
        json.dump(data, file, indent=2)


def load(filename):
    with open(filename + ".json", "r") as file:
        data = json.load(file)
    return data


def delete(filename):
    os.remove(filename + ".json")


def check_exists(filename):
    return os.path.isfile(filename)


def load_map_format(map_file):
    with open(map_file, "r") as file:
        grid = file.read().split("\n")
        grid = [i.replace(",", "") for i in grid]

    # Converting for referencing as [row][col] as split by "/n" gives [col][row]
    new_grid = []
    for row in range(constants.MAP_SIZE[0]):
        new_grid.append([])
        for col in grid:
            new_grid[len(new_grid) - 1].append(col[row])

    return new_grid

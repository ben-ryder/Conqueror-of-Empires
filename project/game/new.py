# Ben-Ryder 2019

import os
import random

import constants
import paths
import project.data as data


# Make a new game, by adding the base data to the json save format.
def make(game_name, map_name, players):

    # Generating Game Data
    game_data = {
        "game_name": game_name,
        "map_name": map_name,
        "game_end": False,
        "current_player": None,  # will be generated on load.
        "players": [get_player_data(player["name"], player["colour"]) for player in players],
        "world": get_world_data(map_name)
    }

    game_data = assign_spawns(game_data)

    # Creating 'saved' directory if it doesn't exist.
    if not os.path.exists(paths.gamePath):
        os.mkdir(paths.gamePath)

    data.save(game_data, paths.gamePath + game_name)


def get_player_data(player_name, player_colour):
    return {
        "name": player_name,
        "colour": player_colour,
        "camera_focus": [None, None],  # will be generated on load.
        "show_minimap": True,

        "units": [],
        "settlements": [],

        "turn": 0,
        "ap": 0,
        "dead": False,
        "max_score": 0
        }


def get_world_data(map_name):
    world_data = {
        "format": data.load_map_format(paths.mapPath + map_name + ".csv"),
    }
    world_data["tiles"] = get_world_tiles_data(world_data["format"])

    return world_data


class CityPicker:
    """ used to randomly assign names to cities """
    def __init__(self):
        # Load Name Choices
        with open(paths.dataPath + "city_names") as file:
            self.name_choices = file.read().split("\n")

    def get_new(self):
        choice = random.choice(self.name_choices)
        self.name_choices.remove(choice)
        return choice


def get_world_tiles_data(map_format):

    city_names = CityPicker()  # A small wrapper around the city_names file allowing the selection of unique names.

    # Make Tiles
    tiles = []
    for row in range(len(map_format[0])):  # assumes col 0, is same len as all others!
        tiles.append([])

        for col in range(len(map_format)):
            tile_type = map_format[row][col]
            tile_position = [row, col]

            if tile_type == "c":
                tiles[-1].append({
                    "type": tile_type,
                    "position": tile_position,

                    "name": city_names.get_new(),
                    "current_holder": None,
                    "level": 1,
                    "sub_level": 0,
                    "max_level": len(constants.LEVELS),
                })
            else:
                tiles[-1].append({
                    "type": tile_type,
                    "position": tile_position
                })

    return tiles


def assign_spawns(game_data):
    spawn_choices = [tile["position"] for row in game_data["world"]["tiles"] for tile in row if tile["type"] == "c"]
    for player in game_data["players"]:
        city_position = random.choice(spawn_choices)
        spawn_choices.remove(city_position)

        # There is a two way relationship, so both must know of each other.
        player["settlements"].append(city_position)
        game_data["world"]["tiles"][city_position[0]][city_position[1]]["current_holder"] = player["name"]

    return game_data

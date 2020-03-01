# Ben-Ryder 2019

import os

import project.game.model as model
import project.data as data
import paths


def make(game_name, map_name,  players):
    """ where players = [[name, colour], [name,colour]...]"""
    game = model.Model(game_name, map_name, players)  # creates "blank" game

    # Creating 'saved' directory if it doesn't exist.
    if not os.path.exists(paths.gamePath):
        os.mkdir(paths.gamePath)

    data.save(game, paths.gamePath + game_name)

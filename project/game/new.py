# Ben-Ryder 2019

import project.game.model as model
import project.data as data
import paths


def make(game_name, map_name,  players):
    """ where players = [[name, colour], [name,colour]...]"""
    game = model.Model(game_name, map_name, players)  # creates "blank" game
    data.save(game, paths.gamePath + game_name)

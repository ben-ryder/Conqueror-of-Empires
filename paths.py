"""
A constants file to export file paths used in the application.
This includes data and asset paths.

This module exports:
    dataPath - The base folder that stores game data such as maps, game saves etc.
    assetPath - The base folder that stores game assets.
    gamePath - The folder that stores saved games.
    mapPath - The folder that stores map files.
    fontPath - The folder that stores font files used in the application.
    imagePath - The base path that stores image assets used in the application.
    tilePath - The folder that stores map tile images.
    unitPath - The folder that stores unit images.
    uiPath - The folder that stores general images related to the application UI.
    uiMenuPath - The folder that stores UI images specifically for the menus.
    uiGamePath - The folder that stores UI images specifically for use in the game.
"""

import os

dataPath = os.getcwd() + os.sep + "data" + os.sep
assetPath = os.getcwd() + os.sep + "assets" + os.sep

gamePath = dataPath + "saved" + os.sep
mapPath = dataPath + "maps" + os.sep

fontPath = assetPath + "fonts" + os.sep
imagePath = assetPath + "images" + os.sep

tilePath = imagePath + "tiles" + os.sep
unitPath = imagePath + "units" + os.sep

uiPath = imagePath + "UI" + os.sep  # general, throughout sections.
uiMenuPath = imagePath + "menu" + os.sep
uiGamePath = imagePath + "game" + os.sep

"""
A file to export constants used throughout the application.

This module exports:
    VERSION - The game version of the current code.
    DISPLAY_NAME - The window title.
    DISPLAY_SIZE - The fixed size of the display.

    MAP_SIZE - The x by y size of the game maps, in tiles.
    TILE_WIDTH - The width of game tiles in px.
    TILE_HEIGHT - The height of game tiles in px.

    MAP_WIDTH - The total map width, worked out from the MAP_SIZE and TILE_WIDTH.
    MAP_HEIGHT - The total map height, worked out from the MAP_SIZE and TILE_WIDTH.
    MAP_PADDING - An arbitrary value for padding around the map.

    GAME_RECT - The rect value ([x, y, width, height]) of the map, including padding.
    ORIGIN - The exact top point of the isometric map.

    COLOURS - A dictionary of colours used throughout the application.
    FONTS - A dictionary of font information used in teh application.

    UNIT_SPECS - The data for each unit in the game including health, attach, defense etc.
    LEVELS - A matrix that manages how city level increases work.
"""

import paths

# Application version. Should always match repository tag.
VERSION = "v1.1.1"

# configuration for pygame.display
DISPLAY_NAME = "Conqueror of Empires"
DISPLAY_SIZE = [1000, 700]

# Map Config
MAP_SIZE = [20, 20]  # ? might not be

TILE_WIDTH = 110
TILE_HEIGHT = 55

MAP_WIDTH = TILE_WIDTH*MAP_SIZE[0]
MAP_HEIGHT = TILE_HEIGHT*MAP_SIZE[1]
MAP_PADDING = 20  # space between map and edge of game surface.

WIDTH = MAP_WIDTH + MAP_PADDING * 2
HEIGHT = MAP_HEIGHT + TILE_HEIGHT + MAP_PADDING * 2
X = -MAP_WIDTH / 2
Y = -MAP_PADDING
GAME_RECT = [X, Y, WIDTH, HEIGHT]  # x, y change with scroll anyway

ORIGIN = [GAME_RECT[2]/2 - TILE_HEIGHT + MAP_PADDING, MAP_PADDING]  # top map point

# Global Constants
COLOURS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "yellow": (255, 220, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "indigo": (75, 0, 130),
    "magenta": (255, 0, 255),
}
COLOURS["panel"] = COLOURS["black"]

FONTS = {"main": paths.fontPath + "SourceSansPro-Light.ttf",
         "main-bold": paths.fontPath + "SourceSansPro-Semibold.ttf",
         "main-italic": paths.fontPath + "SourceSansPro-LightIt.ttf",
         "main-bold-italic": paths.fontPath + "SourceSansPro-SemiboldIt.ttf",
         "sizes":
             {"large": 20,
              "medium": 15,
              "small": 12},
         "colour": COLOURS["white"]}

UNIT_SPECS = {
    "scout": {
        "max_health": 10,
        "attack": 2,
        "defence": 0,
        "reach": 1,
        "movement": 2,

        "spawn_cost": 2,
        "moves": ["g", "f", "c"],
    },
    "swordsman": {
        "max_health": 20,
        "attack": 5,
        "defence": 2,
        "reach": 1,
        "movement": 1,

        "spawn_cost": 5,
        "moves": ["g", "f", "c"],
    },
    "archer": {
        "max_health": 20,
        "attack": 5,
        "defence": 2,
        "reach": 2,
        "movement": 1,

        "spawn_cost": 5,
        "moves": ["g", "f", "c"],
    },
    "horseman": {
        "max_health": 30,
        "attack": 10,
        "defence": 5,
        "reach": 1,
        "movement": 2,

        "spawn_cost": 10,
        "moves": ["g", "f", "c"],
    },
    "catapult": {
        "max_health": 50,
        "attack": 10,
        "defence": 2,
        "reach": 3,
        "movement": 1,

        "spawn_cost": 30,
        "moves": ["g", "f", "c"],
    },
}

# Levels Matrix
# each list item represents a level, each item within a level list represents a sub-level.
LEVELS = [
    [2, 2, 2],  # 1 to 2
    [2, 2, 2, 2],  # 2 to 3
    [2, 2, 2, 2, 2],  # 3 to 4
    [2, 2, 2, 2, 2, 2],  # 4 to 5
    [],  # 5 is max
]

# Cleanup unneeded to not pollute namespace.
del X, Y, WIDTH, HEIGHT, MAP_PADDING

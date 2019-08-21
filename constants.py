# Ben-Ryder 2019

import sys
import subprocess
import paths

# Dev Version Text (Tries for git version, if cant get it, revert to version saved here)
try:
    if sys.version_info[0] < 3.5:
        version = subprocess.check_output(["git", "describe", "--tags"]).strip()
    else:
        version = subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE).stdout.decode("utf-8")
    assert version != ""
except Exception:  # seems to be so dependent on system and versions, easier to do a catch all
    version = "v1.0"  # git not installed, or older lib version, so revert to hardcoded version


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

width = MAP_WIDTH + MAP_PADDING*2
height = MAP_HEIGHT + TILE_HEIGHT + MAP_PADDING*2
x = -MAP_WIDTH/2
y = -MAP_PADDING
GAME_RECT = [x, y, width, height]  # x, y change with scroll anyway

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

# Game Data
TILE_DATA = {
    "s": [0, 0, 0],
    "w": [0, 0, 0],
    "g": [0, 0, 0],
    "f": [100, 20, 5],
    "m": [10, 100, 20],
    "o": [10, 100, 50],
    "c": [100, 50, 25],  # default of settlement store (level 1)
}


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

# each item is level, each item in level is sub-level.
# item: len() = number of sub-levels to next level, value is ap cost to reach sub level/ len() = 0 means max level
# city level starts at 1, to reference level must do city_level - 1.
LEVELS = [
    [2, 2, 2],  # 1 to 2
    [2, 2, 2, 2],  # 2 to 3
    [2, 2, 2, 2, 2],  # 3 to 4
    [2, 2, 2, 2, 2, 2],  # 4 to 5
    [],  # 5 is max
]


# Cleanup unneeded to not pollute namespace.
del x, y, width, height, MAP_PADDING

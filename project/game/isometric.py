# Ben-Ryder 2019

import constants


def getIsoX(row, col):
    return constants.ORIGIN[0] + (row-col) * constants.TILE_WIDTH/2


def getIsoY(row, col):
    return constants.ORIGIN[1] + (row+col) * constants.TILE_HEIGHT/2


def get_iso(row, col, offset):
    isox = getIsoX(row, col)
    isoy = getIsoY(row, col)
    return [isox, isoy]


def getIndex(position, offset):  # an offset is needed because the map is not at 0, 0. I must deal with the scroll.
    tile_ratio = constants.TILE_WIDTH / float(constants.TILE_HEIGHT)
    tile_half_width = constants.TILE_WIDTH/2
    tile_half_height = constants.TILE_HEIGHT/2
    ix = position[0] - offset[0]
    iy = position[1] - offset[1]
    dx = ix - constants.ORIGIN[0] - constants.TILE_WIDTH
    dy = iy - constants.ORIGIN[1] + constants.TILE_HEIGHT/2
    x = int((dy + dx / tile_ratio) * (tile_ratio / 2) / tile_half_width)
    y = int((dy - dx / tile_ratio) * (tile_ratio / 2) / tile_half_width) - 1  # TODO: -1 fix from tests, don't know why!
    return [x, y]

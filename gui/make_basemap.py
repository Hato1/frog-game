import itertools
import random

import pygame as pg

from GAME_CONSTANTS import *
from gui.asset_loader import get_assets, get_spritesheet_dims
from gui.helper import get_sprite_box


def point_in_map(x: int, y: int, map_width: int, map_height: int) -> bool:
    """Check whether a coordinate on a padded map lies in the map"""
    if x not in range(WINDOW_TILE_WIDTH // 2, WINDOW_TILE_WIDTH // 2 + map_width):
        return False
    elif y not in range(WINDOW_TILE_HEIGHT // 2, WINDOW_TILE_HEIGHT // 2 + map_height):
        return False
    else:
        return True


def make_basemap(map_width: int, map_height: int) -> pg.Surface:
    """Creates the background, should run only once per map.

    We pad the map so the void isn't visible past the map edges.

    TODO: Split this into smaller functions
    """
    # map_width, map_height = map_height, map_width
    padded_width = map_width + WINDOW_TILE_WIDTH
    padded_height = map_height + WINDOW_TILE_HEIGHT
    basemap = pg.Surface((padded_width * TSIZE, padded_height * TSIZE))

    assets = get_assets()
    spritesheet_dims = get_spritesheet_dims()

    # TEMP: Default ground tile.
    default_map_tile = "Grass"
    # TEMP: Pad the map with this tile.
    default_padding_tile = "Stone"

    # TODO: Define these somewhere else. Named Tuple?
    plain_tile_index = 0
    particle_index = 11

    for x, y in itertools.product(range(padded_width), range(padded_height)):
        tile_name = (
            default_map_tile if point_in_map(x, y, map_width, map_height) else default_padding_tile
        )

        # Randomly choose which grass tile to draw
        rand_tile = random.randrange(spritesheet_dims[tile_name][plain_tile_index])
        basemap.blit(assets[tile_name], (x * TSIZE, y * TSIZE), get_sprite_box(col=rand_tile))

        # Randomly add fallen leaves
        thresh = 0.25
        while random.random() < thresh:
            rand_tile = random.randrange(spritesheet_dims["Tileset"][particle_index])
            basemap.blit(
                assets["Tileset"],
                (x * TSIZE, y * TSIZE),
                get_sprite_box(particle_index, rand_tile),
            )

            thresh /= 2
    return basemap

import json
from functools import lru_cache

import pygame as pg

from GAME_CONSTANTS import *


def get_dims(tileset: pg.Surface) -> tuple[int, int]:
    """Get the dimensions of a spritesheet"""
    width = tileset.get_width()
    height = tileset.get_height()

    assert width, "invalid dimension"
    assert height, "invalid dimension"
    assert width % TSIZE == 0, f"image height({width}) is not a multiple of {TSIZE}"
    assert height % TSIZE == 0, f"image height({height}) is not a multiple of {TSIZE}"
    return width // TSIZE, height // TSIZE


def create_surface(entity_dict: dict) -> pg.Surface:
    """takes dict retrieved from .json, returns pygame.Surface loaded from correct file"""
    return pg.image.load(f"assets/{entity_dict['FileName']}")


@lru_cache(maxsize=1)
def get_assets() -> dict[str, pg.Surface]:
    """returns asset dictionary from a .json file

    This function is cached with size (1). That means it stores the output from the last
    (1) time it was run with unique arguments. In this case get_assets doesn't take
    arguments so changing cache size has no effect. ~The more you know~
    """
    # Name of json file to retrieve assets from
    map_name = "map1.json"
    path_to_json = f"maps/{map_name}"
    with open(path_to_json) as open_file:
        json_file = json.load(open_file)

    tiles = {tile["Name"]: create_surface(tile) for tile in json_file["Tiles"]}
    entities = {entity["Name"]: create_surface(entity) for entity in json_file["Entities"]}

    return tiles | entities


# define the number of sprites for each texture
# ToDo: I should cache this
@lru_cache(maxsize=1)
def get_spritesheet_dims() -> dict:
    """Returns the number of usable permutations of each image based on the image dims"""
    images = get_assets()
    asset_dims = {}
    for img in images:
        ncols, nrows = get_dims(images[img])
        data = []
        for col in range(ncols):
            empty_spots = 0
            for row in range(nrows):
                # TODO: A simpler way of checking for an empty spritesheet slot
                sprite_surface = (
                    images[img].subsurface(col * TSIZE, row * TSIZE, TSIZE, TSIZE).convert_alpha()
                )
                surface_alpha = pg.transform.average_color(sprite_surface)[-1]
                if surface_alpha == 0:
                    empty_spots = empty_spots + 1
            number_of_states = nrows - empty_spots
            data.append(number_of_states)
        asset_dims[img] = data
    return asset_dims

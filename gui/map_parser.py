"""Module for handling parsing of files created with the world builder for game use"""
# import itertools
import json
import pickle
from pathlib import Path

import pygame as pg

from game.entity import Entity
from game.helper import Point
from GAME_CONSTANTS import *


def get_sprite_box(row: int = 0, col: int = 0) -> tuple[int, int, int, int]:
    """Get the box of a sprite from spritesheet"""
    return row * 25, col * 25, 25, 25


# from tools.builder import cell_interpreter

# Implementation notes for Kiran:
# Currently we use gui.make_basemap to load background from the old map format.
# I'd start by finding out how to load the new world format (See: tools/builder.py)
# then learn the shape of the map format. By that I mean, print it out, index into it, experiment,
# Try to know what everything is & where.
# Finally, implement the below two functions
# The new map format is new, you will encounter issues and find things that could be more efficient.
# Note these things down for later review.
# - Jacob


# def create_surface(entity_dict: dict) -> pg.Surface:
#     """takes dict retrieved from .json, returns pygame.Surface loaded from correct file"""
#     return pg.image.load(f"assets/{entity_dict['FileName']}")
# #@lru_cache(maxsize=1)
# def get_assets() -> dict[str, pg.Surface]:
#     """returns asset dictionary from a .json file
#
#     This function is cached with size (1). That means it stores the output from the last
#     (1) time it was run with unique arguments. In this case get_assets doesn't take
#     arguments so changing cache size has no effect. ~The more you know~
#     """
#     # Name of json file to retrieve assets from
#     map_name = "OLDbuilder.json"
#     path_to_json = f"maps/{map_name}"
#     with open(path_to_json) as open_file:
#         json_file = json.load(open_file)
#
#     tiles = {tile["Name"]: create_surface(tile) for tile in json_file["Tiles"]}
#     entities = {entity["Name"]: create_surface(entity) for entity in json_file["Entities"]}
#
#     return tiles | entities


def load_entities(unparsed_entities_list: list) -> list[Entity]:
    all_entities_list = []
    for x, column in enumerate(unparsed_entities_list):
        for y, tile in enumerate(column):
            for entity in tile:
                # InvisWall not currently supported
                if entity["name"] == "InvisWall":
                    continue
                new_entity_obj = Entity(entity["name"], position=Point(x, y))
                all_entities_list.append(new_entity_obj)

    return all_entities_list


def load_background(base_list: list) -> pg.Surface:
    """
    Builds the basemap from the tile list(s)
    Assumes the background tile is "Stone"
    """
    # TODO: Remove reliance upon the json file maybe
    # pre-load sprites?
    # into another fn?

    world_width = len(base_list[0])
    world_height = len(base_list)

    play_area = pg.Surface((world_width * TSIZE, world_height * TSIZE))

    # Populate the play area
    for y, row in enumerate(base_list):
        for x, space in enumerate(row):
            for tile in space:
                spritesheet = pg.image.load(f"assets/{tile['file_name']}")
                play_area.blit(
                    spritesheet, get_sprite_box(x, y), get_sprite_box(tile["sprite_col"], tile["sprite_row"])
                )

    return play_area
    # It's not important to pad the world so the player can't see the void when close to world edges.
    # padded_width = world_width + WINDOW_TILE_WIDTH
    # padded_height = world_height + WINDOW_TILE_HEIGHT
    # bg = pg.Surface((padded_width * TSIZE, padded_height * TSIZE))
    #
    # for y in range(padded_width):
    #     for x in range(padded_height):
    #
    #
    # return bg


world_name: str | Path = "map1.map"


def add_file_names(base_list: list[dict], entity_list: list[dict]) -> None:
    """Looks at json to find filenames by name, adds to each dict in list"""
    # TODO: Please delete me
    # load the json
    with open("maps/map1.json") as file:
        mdata = json.load(file)

    # build name filename dict
    names_to_filenames = {}
    for dct in mdata["Tiles"]:
        names_to_filenames[dct["Name"]] = dct["FileName"]
    for dct in mdata["Entities"]:
        names_to_filenames[dct["Name"]] = dct["FileName"]

    # Did I write good code jacob?
    # Are you proud of me???
    # for lst in [base_list, entity_list]:
    # for row_I_think in lst:
    #     for col_maybe in row_I_think:
    #         for dct in col_maybe:
    for dct in [a for d in [base_list, entity_list] for c in d for b in c for a in b]:
        dct["file_name"] = names_to_filenames[dct["name"]]
        # replace this hot garbage with a dict("name": pg.surface.Surface)


# Open the world pickle

world_dir = Path("maps")
assert world_dir.exists(), "Can't find world_dir"
world_file = world_dir / world_name
assert world_file.exists(), f"Can't find world file: '{world_file}'"

with open(world_file, "rb") as file:
    base_list, entity_list = pickle.load(file)

# The shit bit where we add the file names to the dict:
add_file_names(base_list, entity_list)

bg = load_background(base_list)
# en = load_entities(entity_list)

pg.init()
screen = pg.display.set_mode(
    (WINDOW_TILE_WIDTH * TSIZE, WINDOW_TILE_HEIGHT * TSIZE),
    pg.SCALED | pg.RESIZABLE,
)

screen.blit(bg, (0, 0))
while True:
    screen.blit(bg, (0, 0))
    pg.display.flip()
# screen.flip()

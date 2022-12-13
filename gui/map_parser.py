"""Module for handling parsing of files created with the world builder for game use"""
# import itertools
import json
import logging
import pickle
from pathlib import Path

import pygame
import pygame as pg

from game.entity import SPECIES, Entity, Facing
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

# TODO: make a fn to load sprites and inject into entity
# TODO: Actually that's probably a bad idea, lets just have a sprites dict in gui.
# This will require redoing how sprites are selected in gui.asset_loader
# Likely a dict with a series of sprites, default requires sprites["idle"]
# could include: facing specific, animation, state specific, all of which requite handling in gui.asset_loader
# def parse_sprites() -> dict[str: list(pygame.surface)]:


def str_to_facing(dir: str) -> Facing:
    # TODO: make this an enum? XD
    match dir:
        case "Up":
            return Facing.UP
        case "Right":
            return Facing.RIGHT
        case "Down":
            return Facing.DOWN
        case "Left":
            return Facing.LEFT
    logging.warning(f"direction {dir} not recognised in map parser")
    return Facing.UP


def load_entities(unparsed_entities_list: list) -> list[Entity]:
    """
    turns the entity lololod into loEntities
    Entities need: name
    """
    all_entities_list = []
    for x, column in enumerate(unparsed_entities_list):
        for y, tile in enumerate(column):
            for dict_entity in tile:
                # InvisWall not currently supported
                if dict_entity["name"] == "InvisWall":
                    continue
                entity_class = SPECIES[dict_entity["name"]]
                new_entity_obj = entity_class(position=Point(x, y))
                # There is definitely a better way to do this, maybe .get(), but that returns Nones
                # @Liam None is False. Time for a walrus? :)
                # What happens when extending a list with None?
                # All entities should have tags even if its empty []
                assert "tags" in dict_entity
                new_entity_obj.tags.extend(dict_entity["tags"])

                assert "direction" in dict_entity
                new_entity_obj._facing = str_to_facing(dict_entity["direction"])
                # new_entity_obj.sprites_dict = parse_sprites()
                all_entities_list.append(new_entity_obj)

    return all_entities_list


def load_background(base_list: list, names_to_spritesheet: dict) -> pg.Surface:
    """
    Builds the basemap from the tile list(s)
    """
    # TODO: Remove reliance upon the json file maybe

    world_width = len(base_list[0])
    world_height = len(base_list)

    play_area = pg.Surface((world_width * TSIZE, world_height * TSIZE))

    # Populate the play area
    for y, row in enumerate(base_list):
        for x, space in enumerate(row):
            for tile in space:
                play_area.blit(
                    names_to_spritesheet[tile["name"]],
                    get_sprite_box(x, y),
                    get_sprite_box(tile["sprite_col"], tile["sprite_row"]),
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


def get_sprites(base_list: list[dict], entity_list: list[dict]) -> dict[str, pg.surface]:
    """
    Looks at json to find filenames by name
    makes a corresponding dict of name: pg.surface
    """
    # load the json
    with open("maps/map1.json") as file:
        mdata = json.load(file)

    # build name filename dict
    names_to_spritesheet = {}
    for dct in mdata["Tiles"]:
        names_to_spritesheet[dct["Name"]] = pg.image.load(f"assets/{dct['FileName']}")
    for dct in mdata["Entities"]:
        names_to_spritesheet[dct["Name"]] = pg.image.load(f"assets/{dct['FileName']}")
    return names_to_spritesheet


def parse_map(world_name) -> tuple[pygame.Surface, list]:
    """loads map pickle, returns basemap and entity list"""
    world_dir = Path("maps")
    assert world_dir.exists(), "Can't find world_dir"
    world_file = world_dir / world_name
    assert world_file.exists(), f"Can't find world file: '{world_file}'"

    with open(world_file, "rb") as file:
        base_list, entity_list = pickle.load(file)

    # The shit bit where we add the file names to the dict:
    names_to_spritesheet = get_sprites(base_list, entity_list)

    bg = load_background(base_list, names_to_spritesheet)
    en = load_entities(entity_list)
    return bg, en


def parse_entities_only(world_name) -> list:
    """loads map pickle, returns entity list"""
    world_dir = Path("maps")
    assert world_dir.exists(), "Can't find world_dir"
    # TODO: Figure out where the extra "maps/" is coming from
    # world_file = world_dir / world_name
    world_file = world_name
    assert world_file.exists(), f"Can't find world file: '{world_file}'"

    with open(world_file, "rb") as file:
        base_list, entity_list = pickle.load(file)

    en = load_entities(entity_list)
    return en


def get_dims(world_name) -> Point:
    world_dir = Path("maps")
    assert world_dir.exists(), "Can't find world_dir"
    # TODO: Figure out where the extra "maps/" is coming from
    # world_file = world_dir / world_name
    world_file = world_name
    assert world_file.exists(), f"Can't find world file: '{world_file}'"
    with open(world_file, "rb") as file:
        base_list, entity_list = pickle.load(file)
    dims = Point(len(entity_list[0]), len(entity_list))
    return dims


#
# # Draw so I can see if the basemap worked
# pg.init()
# screen = pg.display.set_mode(
#     (WINDOW_TILE_WIDTH * TSIZE, WINDOW_TILE_HEIGHT * TSIZE),
#     pg.SCALED | pg.RESIZABLE,
# )
#
# screen.blit(bg, (0, 0))
# while True:
#     screen.blit(bg, (0, 0))
#     pg.display.flip()
# # screen.flip()

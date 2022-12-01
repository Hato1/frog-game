"""Module for handling parsing of files created with the world builder for game use"""
import pickle
from pathlib import Path

import pygame as pg

from game.entity import Entity
from game.helper import Point
from GAME_CONSTANTS import *

world_dir = Path("maps")
assert world_dir.exists(), "Wrong CWD!"

# Implementation notes for Kiran:
# Currently we use gui.make_basemap to load background from the old map format.
# I'd start by finding out how to load the new world format (See: tools/builder.py)
# then learn the shape of the map format. By that I mean, print it out, index into it, experiment,
# Try to know what everything is & where.
# Finally, implement the below two functions
# The new map format is new, you will encounter issues and find things that could be more efficient.
# Note these things down for later review.
# - Jacob


def load_entities(world_name: str | Path) -> list[Entity]:
    world_file = world_dir / world_name
    assert world_file.exists()

    with open(world_file, "rb") as file:
        world = pickle.load(file)

    all_entities_map = world[1]
    all_entities_list = []

    for x, column in enumerate(all_entities_map):
        for y, tile in enumerate(column):
            for entity in tile:
                # InvisWall not currently supported
                if entity["name"] == "InvisWall":
                    continue
                new_entity_obj = Entity(entity["name"], position=Point(x, y))
                all_entities_list.append(new_entity_obj)

    return all_entities_list


def load_background(world: str | Path) -> pg.Surface:
    world = world_dir / world
    assert world.exists()

    # TODO: Get correct dimensions
    world_width = 10
    world_height = 10

    # It's important to pad the world so the player can't see the void when close to world edges.
    padded_width = world_width + WINDOW_TILE_WIDTH
    padded_height = world_height + WINDOW_TILE_HEIGHT
    bg = pg.Surface((padded_width * TSIZE, padded_height * TSIZE))

    return bg


load_entities("map1.map")

"""Module for handling parsing of files created with the world builder for game use"""
from pathlib import Path

import pygame as pg

from game.entity import Entity
from GAME_CONSTANTS import *

world_dir = Path("maps")

# Implementation notes for Kiran:
# Currently we use gui.make_basemap to load background from the old map format.
# I'd start by finding out how to load the new world format (See: tools/builder.py)
# then learn the shape of the map format. By that I mean, print it out, index into it, experiment,
# Try to know what everything is & where.
# Finally, implement the below two functions
# The new map format is new, you will encounter issues and find things that could be more efficient.
# Note these things down for later review.
# -J


def load_entities(world: str | Path) -> list[Entity]:
    world = world_dir / world
    assert world.exists()
    return []


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

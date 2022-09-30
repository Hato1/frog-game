import sys
from pathlib import Path

import pygame as pg

from game.helper import Point
from GAME_CONSTANTS import *


def get_sprite_box(row: int = 0, col: int = 0) -> tuple[int, int, int, int]:
    """Get the box of a sprite from spritesheet"""
    return row * 25, col * 25, 25, 25


def font_render(
    text: str, font_filename: str, color: tuple[int, int, int], font_size: int
) -> pg.surface.Surface:
    font_title = pg.font.Font(Path("assets", font_filename), font_size)
    return font_title.render(text, True, (130, 20, 60))


def get_disp(x: int, y: int) -> tuple[int, int, int, int]:
    """Get the window-sized box centering the coordinate"""

    # To Center the box, we actually don't need to do anything.
    # This is because the basemap is padded WINDOW_COLUMNS on the left
    # and WINDOW_ROWS on the right. This is probably bad practise.
    return (
        x * TSIZE,
        y * TSIZE,
        WINDOW_TILE_WIDTH * TSIZE,
        WINDOW_TILE_HEIGHT * TSIZE,
    )


def coords_to_pixels(point: Point) -> tuple:
    """Convert a tile-space coordinate to pixel-space.

    We have to account for the map buffer tiles.
    """
    return (WINDOW_TILE_WIDTH / 2 + point.x) * TSIZE, (WINDOW_TILE_HEIGHT / 2 + point.y) * TSIZE


def exit_game():
    """Exits game"""
    sys.exit()

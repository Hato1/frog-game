import pygame as pg

TSIZE = 25


def get_dims(tileset: pg.Surface) -> tuple[int, int]:
    """Get the dimensions of a spritesheet"""
    width = tileset.get_width()
    height = tileset.get_height()

    assert width, "invalid dimension"
    assert height, "invalid dimension"
    assert (width % TSIZE == 0), f"image height({width}) is not a multiple of {TSIZE}"
    assert (height % TSIZE == 0), f"image height({height}) is not a multiple of {TSIZE}"
    return width//TSIZE, height//TSIZE


def get_sprite_box(row: int = 0, col: int = 0) -> tuple[int, int, int, int]:
    """Get the box of a sprite from spritesheet"""
    return (row * 25, col * 25, 25, 25)

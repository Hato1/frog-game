import pygame as pg
from pathlib import Path

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
    return row * 25, col * 25, 25, 25


def font_render(text: str, font_filename: str, color: tuple[int, int, int], font_size: int) -> pg.surface.Surface:
    font_title = pg.font.Font(Path("assets", font_filename), font_size)
    rendered_font = font_title.render(text, True, (130, 20, 60))
    return rendered_font


# Pull this from .json
assets = {
    "Player": pg.image.load("assets/Frog.png"),
    "Barrel": pg.image.load("assets/Barrel.png"),
    "FrogR": pg.image.load("assets/FrogR.png"),
    "FrogP": pg.image.load("assets/FrogP.png"),
    "FrogY": pg.image.load("assets/FrogY.png"),
    # "Ball": pg.image.load("assets/intro_ball.gif"),
    "Tileset": pg.image.load("assets/Tileset.png"),
    "Grass": pg.image.load("assets/Grass.png"),
    "Stone": pg.image.load("assets/Stone.png"),
    "rockwall": pg.image.load("assets/rockwall.png"),
}


# define the number of sprites for each texture
# I should cache this
def parse_assets(images: dict) -> dict:
    """Returns the number of usable permutations of each image based on the image dims"""
    asset_dims = {}
    for img in images:
        ncols, nrows = get_dims(images[img])
        data = []
        for col in range(ncols):
            empty_spots = 0
            for row in range(nrows):
                # TODO: A simpler way of checking for an empty spritesheet slot
                sprite_surface = images[img].subsurface(col*TSIZE, row*TSIZE, TSIZE, TSIZE).convert_alpha()
                surface_alpha = pg.transform.average_color(sprite_surface)[-1]
                if surface_alpha == 0:
                    empty_spots = empty_spots + 1
            number_of_states = nrows - empty_spots
            data.append(number_of_states)
        asset_dims[img] = data
    return asset_dims

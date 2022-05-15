# gui.py  - displays things
#         - recieves the input
# This will send the input to the game.py
#       Recieve back the new_map
# display the new map
import sys
import pygame
import random
from game import Game
from map import Map
from copy import copy
from helper import assets, UP, LEFT, RIGHT, DOWN
pygame.init()
TSIZE = 25


def return_num_col(tileset: pygame.Surface) -> tuple[int, int]:
    """Get the number of tiles wide/high an image is"""
    height = tileset.get_height()
    width = tileset.get_width()

    assert width, "invalid dimension"
    assert height, "invalid dimension"
    assert (width % TSIZE == 0), f"image height({width}) is not a multiple of {TSIZE}"
    assert (height % TSIZE == 0), f"image height({height}) is not a multiple of {TSIZE}"
    return int(width/TSIZE), int(height/TSIZE)


def parse_assests(images: dict) -> dict:
    """Returns the number of usable permutations of each image based on the image dimention"""
    asset_dims = {}

    for img in images:
        ncol, nrow = return_num_col(images[img])
        data = []
        for col in range(ncol):
            zeros = 0
            for row in range(nrow):
                sprite_surface = images[img].subsurface(col*TSIZE, row*TSIZE, TSIZE, TSIZE).convert_alpha()
                surface_alpha = pygame.transform.average_color(sprite_surface)[-1]
                if surface_alpha == 0:
                    zeros = zeros + 1
            number_of_states = nrow - zeros
            data.append(number_of_states-1)
        asset_dims[img] = data
    return asset_dims


def process_event(event: pygame.event.Event, game: Game) -> None:
    """Accepts user input

    W: move up
    A: move left
    S: move down
    D: move right
    Q: quits the game
    """
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q:
            sys.exit()
        if event.key in [pygame.K_w, pygame.K_UP]:
            game.move(UP)
        elif event.key in [pygame.K_a, pygame.K_LEFT]:
            game.move(LEFT)
        elif event.key in [pygame.K_s, pygame.K_DOWN]:
            game.move(DOWN)
        elif event.key in [pygame.K_d, pygame.K_RIGHT]:
            game.move(RIGHT)



def sprite_frame(row: int, col: int = 0) -> tuple[int, int, int, int]:
    """takes a tuple, nrow,ncol"""
    return (col * 25, row * 25, 25, 25)


def inds_to_basemap(row: int, col: int) -> tuple:
    """takes row and column on sprite map and returns pixel coordinates on basemap"""
    """and of course, row is col and col is row"""
    offset = ((8 + col) * 25,
              4 * 25 + row * 25)
    return offset


def get_disp(frogloc: tuple[int, int]) -> tuple[int, int, int, int]:
    """takes players location, returns the pixel corners on basemap to display"""
    frogx = (frogloc[1] + 8) * 25 - 188
    froggy = (frogloc[0] + 4 - 4) * 25
    return (frogx, froggy, frogx + 16 * 25, froggy + 9 * 25)


def is_in_play(row: int, col: int, obj_nrow: int, obj_ncol: int) -> bool:
    """this finds if a row/col pair (basemap coords) is in the play area"""
    return row in range(8, 8 + obj_nrow) and col in range(4, 4 + obj_ncol)


def make_basemap(c_map: Map) -> pygame.Surface:
    """creates the background, should run once"""
    # nrow is number of elements in a row
    obj_nrow = len(c_map)
    # ncol is number of elements in a col
    obj_ncol = len(c_map[0])

    # This is the nmber of columns/nmber of elements in each row
    wld_nrow = obj_nrow + 16
    # This is the number of rows
    wld_ncol = obj_ncol + 8

    # Initialises the entire basemap (width, height)
    basemap = pygame.Surface((wld_nrow * 25, wld_ncol * 25))

    # ###This is probably bad, but is fone for now
    # tileset_playarea = 1
    # tileset_oob = 6

    # Pull this from c_map eventually
    tileset_playarea = "Grass"
    tileset_oob = "Stone"

    # define the number of sprites for each texture
    dims = parse_assests(assets)

    # Pretty sure row is col and col is row
    for row in range(wld_nrow):
        for col in range(wld_ncol):
            in_play = is_in_play(row, col, obj_nrow, obj_ncol)
            if in_play:
                ts = tileset_playarea
            else:
                ts = tileset_oob

            rand_tile = random.randint(0, dims["Stone"][0])  # <--------- This is where we make cliffs
            basemap.blit(assets[ts],
                       (row * 25, col * 25),
                       sprite_frame(rand_tile, 0))  # <--------- This is where we make cliffs
            rand_tile = random.randint(0, 15)
            basemap.blit(assets["Tileset"],
                       (row * 25, col * 25),
                       sprite_frame(rand_tile, 11))

    return basemap


def make_current_frame(c_map: Map, basemap: pygame.Surface, ) -> pygame.Surface:
    """ adds sprites to the basemap"""
    # nrow is number of elements in a row
    obj_nrow = len(c_map)
    # ncol is number of elements in a col
    obj_ncol = len(c_map[0])

    # # This is the nmber of columns/nmber of elements in each row
    # wld_nrow = obj_nrow + 16
    # # This is the number of rows
    # wld_ncol = obj_ncol + 8

    for row in range(obj_nrow):
        for col in range(obj_ncol):
            for k in c_map[row][col]:
                basemap.blit(assets[k.name], inds_to_basemap(row, col), sprite_frame(0))

    return basemap


def guiloop() -> None:
    # Initialising stuff
    # size of window
    size = width, height = 16 * 25, 9 * 25
    game = Game()
    screen = pygame.display.set_mode(size, pygame.SCALED | pygame.RESIZABLE)

    # Load the map
    c_map = game.get_map()
    basemap = make_basemap(c_map)

    while True:
        for event in pygame.event.get():
            process_event(event, game)
        # other conditions here

        # update map thing here
        c_map = game.get_map()
        current_frame = make_current_frame(c_map, copy(basemap))

        # find frog and display
        froglocation, null = c_map.find_object("Player")
        screen.blit(current_frame, (0, 0), get_disp(froglocation))
        pygame.display.flip()


guiloop()

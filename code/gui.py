"""Viewer/Controller model for Frog Game.

Controller:
    Accepts user input which is parsed to send to Frog Game.
Viewer:
    Shows a visual representation of the game state.

Height/Width refer to pixel values to be displayed.
Rows/Columns are coordinates in the game map/grid.
"""
import sys
import pygame
import random
from game import Game
from map import Map
from copy import copy
from helper import assets, UP, LEFT, RIGHT, DOWN
from gui_helper import get_dims, get_sprite_box

# Asset tile size
TSIZE = 25
WINDOW_ROWS = 9
WINDOW_COLUMNS = 16
ANIMATIONS = True

pygame.init()


def parse_assets(images: dict) -> dict:
    """Returns the number of usable permutations of each image based on the image dims"""
    asset_dims = {}
    for img in images:
        ncol, nrow = get_dims(images[img])
        data = []
        for col in range(ncol):
            empty_spots = 0
            for row in range(nrow):
                # TODO: A simpler way of checking for an empty spritesheet slot
                sprite_surface = images[img].subsurface(col*TSIZE, row*TSIZE, TSIZE, TSIZE).convert_alpha()
                surface_alpha = pygame.transform.average_color(sprite_surface)[-1]
                if surface_alpha == 0:
                    empty_spots = empty_spots + 1
            number_of_states = nrow - empty_spots
            data.append(number_of_states)
        asset_dims[img] = data
    return asset_dims


def process_event(event: pygame.event.Event, game: Game) -> bool:
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
            return game.move(UP)
        elif event.key in [pygame.K_a, pygame.K_LEFT]:
            return game.move(LEFT)
        elif event.key in [pygame.K_s, pygame.K_DOWN]:
            return game.move(DOWN)
        elif event.key in [pygame.K_d, pygame.K_RIGHT]:
            return game.move(RIGHT)
    return False


def coords_to_pixels(row: int, col: int) -> tuple:
    """takes row and column on sprite map and returns pixel coordinates on basemap
    and of course, row is col and col is row"""
    offset = ((8 + col) * TSIZE,
              4 * TSIZE + row * TSIZE)
    return offset


def get_disp(y: int, x: int) -> tuple[int, int, int, int]:
    """Get the window-sized box centering the coordinate

    TODO: Clean this up for any window size."""

    # Since this function is for working on the padded basemap,
    # We should account for that. Need a better solution!
    x = x + WINDOW_COLUMNS/2
    y = y + WINDOW_ROWS/2

    # Not sure why the left edge has to be pushed 0.5
    return (
        (x - WINDOW_COLUMNS/2 + 0.5) * TSIZE,
        (y - WINDOW_ROWS/2) * TSIZE,
        (x + WINDOW_COLUMNS/2) * TSIZE,
        (y + WINDOW_ROWS/2) * TSIZE
    )


def make_basemap(c_map: Map) -> pygame.Surface:
    """creates the background, should run once

    TODO: Extract variables ending in INDEX elsewhere...
    TODO: Is it good or bad style to nest functions where possible?
    """
    def is_in_play(row: int, col: int, nrows: int, ncols: int) -> bool:
        """Check whether a coordinate on a padded map lies in the map"""
        return row in range(8, 8 + ncols) and col in range(4, 4 + nrows)

    map_ncols = c_map.get_ncols()
    map_nrows = c_map.get_nrows()

    # The map is padded such that the user won't be able to see out of bounds.
    # The actual map will be placed in the center of the padded map.
    padded_map_ncols = map_ncols + WINDOW_COLUMNS
    padded_map_nrows = map_nrows + WINDOW_ROWS
    basemap = pygame.Surface((padded_map_ncols * TSIZE, padded_map_nrows * TSIZE))

    # TODO: Map objects should map backgrounds. Let's pull this from c_map eventually.
    tileset_playarea = "Grass"
    tileset_oob = "Stone"

    # define the number of sprites for each texture
    dims = parse_assets(assets)

    for row in range(padded_map_ncols):
        for col in range(padded_map_nrows):
            if is_in_play(row, col, map_nrows, map_ncols):
                ts = tileset_playarea
            else:
                ts = tileset_oob
            # Randomise which column the tile is taken from.
            PLAIN_TILE_INDEX = 0
            rand_tile = random.randrange(dims[ts][PLAIN_TILE_INDEX])
            basemap.blit(assets[ts],
                         (row * TSIZE, col * TSIZE),
                         get_sprite_box(col=rand_tile))
            # 25% chance of adding a random particle to a tile.
            if random.random() < 0.25:
                PARTICLE_INDEX = 11
                rand_tile = random.randrange(dims["Tileset"][PARTICLE_INDEX])
                basemap.blit(assets["Tileset"],
                             (row * TSIZE, col * TSIZE),
                             get_sprite_box(11, rand_tile))

    return basemap


def make_current_frame(c_map: Map, basemap: pygame.Surface, ) -> pygame.Surface:
    """Draws entities on basemap"""
    # TODO: Make a nicer way of iterating through map objects while keeping the indexes
    for row in range(c_map.get_nrows()):
        for col in range(c_map.get_ncols()):
            for entity in c_map[row][col]:
                sprite = assets[entity.name]
                # TODO: Rotation breaks when not using first image of spritesheet,
                # as the entire image is rotated. Current hacky workaround is to only
                # rotate Creatures
                if str(type(entity)) == "<class 'entity.Creature'>":
                    sprite = pygame.transform.rotate(sprite, 90*entity.direction)
                basemap.blit(
                    sprite,
                    coords_to_pixels(row, col),
                    get_sprite_box()
                )
    return basemap


def pan_screen(
    current_frame: pygame.Surface,
    screen: pygame.surface.Surface,
    oldmap: Map,
    newmap: Map,
    oldcenter: tuple[int, int],
    newcenter: tuple[int, int]
) -> None:
    """Smoothly pan the screen from old to new center

    TODO: Slide creatures from oldmap position to newmap position (Warning: Hard)
    """
    speed = 4
    ydiff = int(newcenter[0] - oldcenter[0])
    xdiff = int(newcenter[1] - oldcenter[1])
    disp = get_disp(*oldcenter)
    for i in range(speed):
        xpos = int(disp[0] + xdiff * TSIZE * (i/speed))
        ypos = int(disp[1] + ydiff * TSIZE * (i/speed))
        screen.blit(current_frame, (0, 0), (xpos, ypos, disp[2], disp[3]))
        pygame.display.flip()
        pygame.time.wait(15)


def guiloop() -> None:
    # Initialising stuff
    game = Game()
    screen = pygame.display.set_mode((WINDOW_COLUMNS*TSIZE, WINDOW_ROWS*TSIZE), pygame.SCALED | pygame.RESIZABLE)

    # Load the map. This will be a function when we have multiple maps tp go between.
    c_map = game.get_map()
    froglocation, null = c_map.find_object("Player")
    basemap = make_basemap(c_map)
    map_changed = True

    while True:
        # Update game
        if map_changed:
            new_map = game.get_map()
            current_frame = make_current_frame(new_map, copy(basemap))
            new_froglocation, null = new_map.find_object("Player")

            if ANIMATIONS and froglocation != new_froglocation:
                pan_screen(current_frame, screen, c_map, new_map, froglocation, new_froglocation)

            # find frog and display
            screen.blit(current_frame, (0, 0), get_disp(*new_froglocation))
            pygame.display.flip()
            map_changed = False

            c_map = new_map
            froglocation = new_froglocation

        # Resolve pending user inputs
        for event in pygame.event.get():
            if process_event(event, game):
                map_changed = True


guiloop()

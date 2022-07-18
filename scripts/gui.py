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
import math
import time
import logging

from pathlib import Path
from .game import Game
from .map import Map
from .entity import Creature
from copy import copy
from .helper import UP, LEFT, RIGHT, DOWN
from .gui_helper import get_sprite_box, assets, parse_assets

# Asset tile size
TSIZE = 25
WINDOW_ROWS = 9
WINDOW_COLUMNS = 16
ANIMATIONS = True

# Enable to print frametimes to console.
BENCHMARK = False

pygame.init()
logging.basicConfig(level=1, format='')


def process_event(event: pygame.event.Event, game: Game) -> bool:
    """Accepts user input

    W: move up
    A: move left
    S: move down
    D: move right
    Q: quits the game
    R: kills the player (Restart)
    """
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q:
            sys.exit()
        if event.key == pygame.K_r:
            game.player = False

        if game.player:
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


def get_disp(x: int, y: int) -> tuple[int, int, int, int]:
    """Get the window-sized box centering the coordinate

    TODO: Clean this up for any window size.
    """

    # Why?
    x, y = y, x

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
    global spritesheet_dims
    spritesheet_dims = parse_assets(assets)

    for row in range(padded_map_ncols):
        for col in range(padded_map_nrows):
            if is_in_play(row, col, map_nrows, map_ncols):
                ts = tileset_playarea
            else:
                ts = tileset_oob
            # Randomise which column the tile is taken from.
            PLAIN_TILE_INDEX = 0
            rand_tile = random.randrange(spritesheet_dims[ts][PLAIN_TILE_INDEX])
            basemap.blit(assets[ts],
                         (row * TSIZE, col * TSIZE),
                         get_sprite_box(col=rand_tile))
            # 25% chance of adding a random particle to a tile.
            if random.random() < 0.25:
                PARTICLE_INDEX = 11
                rand_tile = random.randrange(spritesheet_dims["Tileset"][PARTICLE_INDEX])
                basemap.blit(assets["Tileset"],
                             (row * TSIZE, col * TSIZE),
                             get_sprite_box(11, rand_tile))

    return basemap


def make_current_frame(c_map: Map, basemap: pygame.Surface, player_alive: bool, frame: int) -> pygame.Surface:
    """Draws entities on basemap"""
    # TODO: Make a nicer way of iterating through map objects while keeping the indexes
    # for row in range(c_map.get_nrows()):
    #     for col in range(c_map.get_ncols()):
    #         for entity in c_map[row][col]:
    animation_stage = [0, 2, 3][(frame) % 3]
    #animation_stage = random.choice([0, 2, 3])
    for pos, entities in c_map._iterate():
        for entity in entities:
            if not player_alive and entity.name == "Player":
                continue
            sprite = assets[entity.name]
            sprite_index = (0, 0)
            # TODO: Rotation breaks when not using first image of spritesheet,
            # as the entire image is rotated. Current hacky workaround is to only
            # rotate Creatures
            if type(entity) == Creature:
                sprite_index = (0, animation_stage)
                creature_sprite = pygame.Surface((25, 25))
                creature_sprite.fill((255, 255, 255))
                creature_sprite.set_colorkey('white')
                creature_sprite.blit(
                    sprite,
                    (0, 0),
                    get_sprite_box(*sprite_index)
                )
                creature_sprite = pygame.transform.rotate(creature_sprite, 90*entity.direction)
                basemap.blit(
                    creature_sprite,
                    coords_to_pixels(*pos)
                )
            else:
                if entity.name == "Stone":
                    # TODO: Delete this hacky fix to prevent rock textures randomising.
                    # TODO: Stone should be a part of basemap to improve fps.
                    random.seed(f"{pos}")
                    PLAIN_TILE_INDEX = 0
                    spritenum = random.randrange(
                        spritesheet_dims["Stone"][PLAIN_TILE_INDEX])
                    sprite_index = (PLAIN_TILE_INDEX, spritenum)
                    random.seed()
                basemap.blit(
                    sprite,
                    coords_to_pixels(*pos),
                    get_sprite_box(*sprite_index)
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
    Best to keep move history in entities and read the newmap and most recent move.
    """
    speed = 5
    ydiff = int(newcenter[0] - oldcenter[0])
    xdiff = int(newcenter[1] - oldcenter[1])
    disp = get_disp(*oldcenter)
    for i in range(speed):
        xpos = int(disp[0] + xdiff * TSIZE * (i/speed))
        ypos = int(disp[1] + ydiff * TSIZE * (i/speed))
        screen.blit(current_frame, (0, 0), (xpos, ypos, disp[2], disp[3]))
        pygame.display.flip()
        pygame.time.wait(20)


def guiloop(screen) -> None:
    last_frame_time = pygame.time.get_ticks()
    old_time = pygame.time.get_ticks()
    now = old_time
    game = Game()
    # Load the map. This will be a function when we have multiple maps to go between.
    c_map = game.get_map()
    froglocation, null = c_map.find_object("Player")
    basemap = make_basemap(c_map)
    current_map = None
    map_changed = True
    frame = 0
    while True:
        if not BENCHMARK:
            difference = -old_time + (old_time := pygame.time.get_ticks())
            logging.debug(msg=difference)
        # Update game
        # Set max fps to 30 (33ms).
        if map_changed or (now := pygame.time.get_ticks()) - last_frame_time > 750:
            last_frame_time = now
            frame += 1
            new_map = game.get_map()
            current_frame = make_current_frame(new_map, copy(basemap), game.player, frame)
            new_froglocation, null = new_map.find_object("Player")

            # Could boost fps by multiprocessing collision alongside the animation?
            if ANIMATIONS and froglocation != new_froglocation:
                pan_screen(
                    current_frame, screen, c_map, new_map, froglocation, new_froglocation
                )

        # find player (frog) and blit map around player
        screen.blit(current_frame, (0, 0), get_disp(*new_froglocation))
        current_map = current_frame

        pygame.display.flip()
        map_changed = False

        c_map = new_map
        froglocation = new_froglocation

        # This is incredibly ugly, needs rewrite.
        # Have text fade in, possibly have buttons unresponsive
        # for about 0.2 seconds so player doesn't skip death screen.
        # darken background (current_map) so it's clear you can't interact.
        # B&W filter instead of darken background?
        # Sound effect here would be great!
        if not game.player:
            break

        # Resolve pending user inputs
        for event in pygame.event.get():
            if process_event(event, game):
                map_changed = True

    # Player dead
    magic_number = 0
    while True:
        pygame.time.delay(50)
        font_title = pygame.font.Font(Path("assets", "Amatic-Bold.ttf"), 36 * 3)
        you_died = font_title.render("You  Died", 1, (130, 20, 60))
        you_died = pygame.transform.rotate(you_died, math.sin(time.time() / 1.5) * 10)
        you_died = pygame.transform.scale(
            you_died,
            (
                you_died.get_width() + int(math.sin(time.time() / 1) * 20),
                you_died.get_height() + int(math.sin(time.time() / 1) * 20),
            ),
        )
        you_died_pos = you_died.get_rect(
            centerx=screen.get_width() / 2,
            centery=screen.get_height() / 3,
        )
        any_key_font = pygame.font.Font(Path("assets", "Amatic-Bold.ttf"), 25)
        any_key = any_key_font.render("(Press any key to continue)", 255, (130, 20, 60))
        any_key_pos = any_key.get_rect(
            centerx=screen.get_width() / 2,
            centery=screen.get_height() * 5 / 6,
        )

        white = pygame.Surface(screen.get_size())

        screen.blit(current_map, (0, 0), get_disp(*new_froglocation))

        white.set_alpha(min((magic_number*3 - 100), 200))
        screen.blit(white, (0, 0))
        you_died.set_alpha(magic_number*5)
        screen.blit(you_died, you_died_pos)
        any_key.set_alpha(magic_number*3 - 100)
        screen.blit(any_key, any_key_pos)
        pygame.display.flip()

        if any(event.type == pygame.KEYDOWN for event in pygame.event.get()):
            return
        magic_number += 1


def main():
    # Initialising stuff
    screen = pygame.display.set_mode(
        (WINDOW_COLUMNS*TSIZE, WINDOW_ROWS*TSIZE),
        pygame.SCALED | pygame.RESIZABLE
    )
    while True:
        guiloop(screen)


main()

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
from .helper import UP, LEFT, RIGHT, DOWN, Benchmark
from .gui_helper import get_sprite_box, assets, parse_assets, font_render

# Asset tile size
TSIZE: int = 25
WINDOW_ROWS = 9
WINDOW_COLUMNS = 16
ANIMATIONS = True

# Enable to print frametimes to console.
# TODO: Make this a commandline argument
BENCHMARK = False
if BENCHMARK:
    benchmark = Benchmark()

pygame.init()
logging.basicConfig(level=1, format='')

spritesheet_dims: dict


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
            game.kill_player()

        if game.is_player_alive():
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
    and of course, row is col and col is row

    returns: Offset?"""
    return (8 + col) * TSIZE, 4 * TSIZE + row * TSIZE


def get_disp(x: int, y: int) -> tuple[int, int, int, int]:
    """Get the window-sized box centering the coordinate"""
    # I think X and Y are backwards. Pygame implementation??

    # To Center the box, we actually don't need to do anything.
    # This is because the basemap is padded WINDOW_COLUMNS on the left
    # and WINDOW_ROWS on the right. This is probably bad practise.

    # Not sure why the left edge has to be pushed 0.5
    return (
        y * TSIZE + TSIZE//2,
        x * TSIZE,
        WINDOW_COLUMNS * TSIZE,
        WINDOW_ROWS * TSIZE,
    )


def is_in_play(row: int, col: int, nrows: int, ncols: int) -> bool:
    """Check whether a coordinate on a padded map lies in the map"""
    return row in range(8, 8 + ncols) and col in range(4, 4 + nrows)


def make_basemap(c_map: Map) -> pygame.Surface:
    """creates the background, should run once

    TODO: Extract variables ending in INDEX elsewhere...
    TODO: Is it good or bad style to nest functions where possible?
    """
    map_ncols = c_map.get_ncols()
    map_nrows = c_map.get_nrows()
    padded_map_ncols = map_ncols + WINDOW_COLUMNS
    padded_map_nrows = map_nrows + WINDOW_ROWS
    basemap = pygame.Surface((padded_map_ncols * TSIZE, padded_map_nrows * TSIZE))
    tileset_play_area = "Grass"
    tileset_oob = "Stone"
    global spritesheet_dims
    spritesheet_dims = parse_assets(assets)
    plain_tile_index = 0
    particle_index = 11
    for row in range(padded_map_ncols):
        for col in range(padded_map_nrows):
            ts = tileset_play_area if is_in_play(row, col, map_nrows, map_ncols) else tileset_oob

            rand_tile = random.randrange(spritesheet_dims[ts][plain_tile_index])
            basemap.blit(assets[ts], (row * TSIZE, col * TSIZE), get_sprite_box(col=rand_tile))

            thresh = 0.25
            while random.random() < thresh:
                rand_tile = random.randrange(spritesheet_dims["Tileset"][particle_index])
                basemap.blit(assets["Tileset"], (row * TSIZE, col * TSIZE), get_sprite_box(11, rand_tile))

                thresh /= 2
    return basemap


class HudElement:
    # Make this a named tuple?
    def __init__(self, source: pygame.surface.Surface, dest: tuple) -> None:
        self.source = source
        self.dest = dest


class Hud:
    def __init__(self) -> None:
        self.elements: dict = {}

    def update_element(self, name: str, source: pygame.surface.Surface, dest: tuple) -> None:
        """both adds and updates elements"""
        self.elements.update({name: HudElement(source, dest)})

    def get_elements(self) -> tuple:
        """returns a list to be used by blits"""
        return tuple(
            (element.source, element.dest)
            for element in self.elements.values()
        )


def add_hud(screen: pygame.surface.Surface, hud: Hud) -> None:
    screen.blits(hud.get_elements())


def draw_map(c_map: Map, basemap: pygame.Surface, draw_player: bool, frame: int) -> pygame.Surface:
    """Draws entities on basemap"""
    # TODO: Make a nicer way of iterating through map objects while keeping the indexes
    # for row in range(c_map.get_nrows()):
    #     for col in range(c_map.get_ncols()):
    #         for entity in c_map[row][col]:
    animation_stage = [0, 2, 3][frame % 3]
    # animation_stage = random.choice([0, 2, 3])
    for pos, entities in c_map.iterate():
        for entity in entities:
            if entity.name == "Player" and not draw_player:
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
                    plain_tile_index = 0
                    global spritesheet_dims
                    sprite_num = random.randrange(
                        spritesheet_dims["Stone"][plain_tile_index])
                    sprite_index = (plain_tile_index, sprite_num)
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
    hud: Hud,
    old_center: tuple[int, int],
    new_center: tuple[int, int]
) -> None:
    """Smoothly pan the screen from old to new center

    TODO: Slide creatures from old_map position to new_map position (Warning: Hard)
    Best to keep move history in entities and read the new_map and most recent move.
    """
    speed = 5
    ydiff = int(new_center[0] - old_center[0])
    xdiff = int(new_center[1] - old_center[1])
    disp = get_disp(*old_center)
    for i in range(speed):
        xpos = int(disp[0] + xdiff * TSIZE * (i/speed))
        ypos = int(disp[1] + ydiff * TSIZE * (i/speed))
        screen.blit(current_frame, (0, 0), (xpos, ypos, disp[2], disp[3]))
        add_hud(screen, hud)
        pygame.display.flip()
        pygame.time.wait(20)


def play_death_animation(
        screen: pygame.surface.Surface,
        current_frame: pygame.surface.Surface,
        new_froglocation: tuple
) -> None:
    # Player dead

    # This is incredibly ugly, needs rewrite.
    # Have text fade in, possibly have buttons unresponsive
    # for about 0.2 seconds so player doesn't skip death screen.
    # darken background (current_map) so it's clear you can't interact.
    # B&W filter instead of darken background?
    # Sound effect here would be great!
    magic_number = 0
    while True:
        pygame.time.delay(50)
        you_died = font_render("You  Died", "Amatic-Bold.ttf", (130, 20, 60), 36*3)
        Path()
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
        any_key = font_render("(Press any key to continue)", "Amatic-Bold.ttf", (130, 20, 60), 25)
        any_key_pos = any_key.get_rect(
            centerx=screen.get_width() / 2,
            centery=screen.get_height() * 5 / 6,
        )

        white = pygame.Surface(screen.get_size())

        screen.blit(current_frame, get_disp(*new_froglocation))

        white.set_alpha(min((magic_number*3 - 100), 200))
        screen.blit(white, (0, 0))
        you_died.set_alpha(magic_number*5)
        screen.blit(you_died, you_died_pos)
        any_key.set_alpha(magic_number*3 - 100)
        screen.blit(any_key, any_key_pos)
        pygame.display.flip()

        if magic_number > 20 and any(
                event.type == pygame.KEYDOWN
                for event in pygame.event.get()
        ):
            return
        magic_number += 1


def gui_loop(screen: pygame.surface.Surface) -> None:
    last_frame_time = pygame.time.get_ticks()
    now = pygame.time.get_ticks()
    game = Game()
    # Load the map. This will be a function when we have multiple maps to go between.
    c_map = game.get_map()
    hud = Hud()
    hud.update_element(
        "step_count",
        font_render(
            str(game.map.get_steps_left()),
            "Amatic-Bold.ttf",
            (130, 20, 60), 25
        ),
        (0, 0)
    )
    frog_location = game.get_player_pos()
    basemap = make_basemap(c_map)
    map_changed = True
    frame_count = 0

    # Game loop
    while True:
        if BENCHMARK:
            benchmark.log_time_delta()

        # Update game
        # Set max fps to 30 (33ms).
        if map_changed or (now := pygame.time.get_ticks()) - last_frame_time > 750:
            last_frame_time = now
            frame_count += 1
            new_map = game.get_map()
            frame = draw_map(new_map, copy(basemap), game.is_player_alive(), frame_count)
            new_froglocation = game.get_player_pos()
            if ANIMATIONS and frog_location != new_froglocation:
                pan_screen(frame, screen, hud, frog_location, new_froglocation)
            screen.blit(frame, (0, 0), get_disp(*new_froglocation))
            add_hud(screen, hud)
            pygame.display.flip()

            map_changed = False
            frog_location = new_froglocation
            if not game.is_player_alive():
                break

        # Process Input
        for event in pygame.event.get():
            if process_event(event, game):
                map_changed = True
                hud.update_element(
                    "step_count",
                    font_render(
                        str(game.map.get_steps_left()),
                        "Amatic-Bold.ttf",
                        (130, 20, 60), 25
                    ),
                    (0, 0)
                )
                # Prevent skipping of movement animations
                break
    play_death_animation(screen, frame, new_froglocation)


def main() -> None:
    # Initialising stuff
    screen = pygame.display.set_mode(
        (WINDOW_COLUMNS*TSIZE, WINDOW_ROWS*TSIZE),
        pygame.SCALED | pygame.RESIZABLE
    )
    while True:
        gui_loop(screen)


main()

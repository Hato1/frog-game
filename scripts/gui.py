"""Viewer/Controller model for Frog Game.

Controller:
    Accepts user input which is parsed to send to Frog Game.
Viewer:
    Shows a visual representation of the game state.

Height/Width refer to pixel values to be displayed.
Rows/Columns are coordinates in the game map/grid.
"""
import itertools
import logging
import math
import random
import sys
import time
from collections import namedtuple
from copy import copy
from pathlib import Path

import pygame

from .game import Game
from .gui_helper import assets, font_render, get_sprite_box, parse_assets
from .helper import DOWN, LEFT, RIGHT, UP, Benchmark, Point
from .sound import SoundSystem

# Asset tile size
TSIZE: int = 25
# FIXME: Using even numbered tile dims causes the screen to center 0.5 tiles off
WINDOW_TILE_HEIGHT = 18
WINDOW_TILE_WIDTH = 32
ANIMATIONS = True

# Enable to print frametimes to console.
# TODO: Make this a commandline argument
BENCHMARK = False
if BENCHMARK:
    benchmark = Benchmark()

pygame.init()

logger = logging.getLogger("Frog")


# loads the sound system
sound_system = SoundSystem()

SPRITESHEET_DIMS: dict = {}


def process_event(event: pygame.event.Event, game: Game) -> bool:
    """Accepts user input

    W: move up
    A: move left
    S: move down
    D: move right
    Q: quits the game
    R: kills the player (Restart)

    Returns:
        bool: If movement input was accepted (Screen must be redrawn)
    """
    if event.type == pygame.QUIT:
        exit_game()
    elif event.type == pygame.KEYDOWN:
        match event.key:
            case pygame.K_r:
                game.kill_player()

            case pygame.K_w | pygame.K_UP:
                return game.move(UP)
            case pygame.K_a | pygame.K_LEFT:
                return game.move(LEFT)
            case pygame.K_s | pygame.K_DOWN:
                return game.move(DOWN)
            case pygame.K_d | pygame.K_RIGHT:
                return game.move(RIGHT)
    return False


def process_universal_input(event: pygame.event.Event):
    """feed pygame events to allow the player to perform actions
    that aren't dependent on the players alive status"""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q:
            exit_game()

        elif event.key == pygame.K_m:
            sound_system.toggle_mute()

        elif event.key == pygame.K_p:
            sound_system.toggle_music()


def exit_game():
    """Exits game"""
    sys.exit()


def coords_to_pixels(point: Point) -> tuple:
    """Convert a tile-space coordinate to pixel-space.

    We have to account for the map buffer tiles.
    """
    return (WINDOW_TILE_WIDTH / 2 + point.x) * TSIZE, (
        WINDOW_TILE_HEIGHT / 2 + point.y
    ) * TSIZE


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


def point_in_map(x: int, y: int, map_width: int, map_height: int) -> bool:
    """Check whether a coordinate on a padded map lies in the map"""
    if x not in range(WINDOW_TILE_WIDTH // 2, WINDOW_TILE_WIDTH // 2 + map_width):
        return False
    elif y not in range(WINDOW_TILE_HEIGHT // 2, WINDOW_TILE_HEIGHT // 2 + map_height):
        return False
    else:
        return True


def make_basemap(map_width: int, map_height: int) -> pygame.Surface:
    """Creates the background, should run only once per map.

    We pad the map so the void isn't visible past the map edges.

    TODO: Split this into smaller functions
    """
    # map_width, map_height = map_height, map_width
    padded_width = map_width + WINDOW_TILE_WIDTH
    padded_height = map_height + WINDOW_TILE_HEIGHT
    basemap = pygame.Surface((padded_width * TSIZE, padded_height * TSIZE))

    # TEMP: Default ground tile.
    default_map_tile = "Grass"
    # TEMP: Pad the map with this tile.
    default_padding_tile = "Stone"

    # TODO: Define these somewhere else. Named Tuple?
    plain_tile_index = 0
    particle_index = 11

    for x, y in itertools.product(range(padded_width), range(padded_height)):
        tile_name = (
            default_map_tile
            if point_in_map(x, y, map_width, map_height)
            else default_padding_tile
        )

        # Randomly choose which grass tile to draw
        rand_tile = random.randrange(SPRITESHEET_DIMS[tile_name][plain_tile_index])
        basemap.blit(
            assets[tile_name], (x * TSIZE, y * TSIZE), get_sprite_box(col=rand_tile)
        )

        # Randomly add fallen leaves
        thresh = 0.25
        while random.random() < thresh:
            rand_tile = random.randrange(SPRITESHEET_DIMS["Tileset"][particle_index])
            basemap.blit(
                assets["Tileset"],
                (x * TSIZE, y * TSIZE),
                get_sprite_box(particle_index, rand_tile),
            )

            thresh /= 2
    return basemap


class Hud:
    HudElement = namedtuple("HudElement", "source dest")

    def __init__(self) -> None:
        self.elements: dict = {}

    def update_element(
        self, name: str, source: pygame.surface.Surface, dest: tuple
    ) -> None:
        """both adds and updates elements"""
        self.elements.update({name: self.HudElement(source, dest)})

    def get_elements(self) -> tuple:
        """returns a list to be used by blits"""
        return tuple(
            (element.source, element.dest) for element in self.elements.values()
        )


def add_hud(screen: pygame.surface.Surface, hud: Hud) -> None:
    screen.blits(hud.get_elements())


def draw_map(
    entities: list, basemap: pygame.Surface, draw_player: bool, frame: int
) -> pygame.Surface:
    """Draws entities on basemap"""
    # TODO: Make a nicer way of iterating through map objects while keeping the indexes

    animation_stage = [0, 2, 3][frame % 3]
    # animation_stage = random.choice([0, 2, 3])
    for entity in entities:
        if entity.name == "Player" and not draw_player:
            continue
        sprite = assets[entity.name]
        sprite_index = (0, 0)
        # TODO: Rotation breaks when not using first image of spritesheet,
        # as the entire image is rotated. Current hacky workaround is to only
        # rotate Creatures
        # TODO: Remove magic strings
        if entity.name not in ["Stone", "rockwall"]:
            sprite_index = (0, animation_stage)
            creature_sprite = pygame.Surface((25, 25))
            creature_sprite.fill((255, 255, 255))
            creature_sprite.set_colorkey("white")
            creature_sprite.blit(sprite, (0, 0), get_sprite_box(*sprite_index))
            creature_sprite = pygame.transform.rotate(
                creature_sprite, 90 * entity.direction
            )
            basemap.blit(creature_sprite, coords_to_pixels(entity.position))
        else:
            if entity.name == "Stone":
                # TODO: Delete this hacky fix to prevent rock textures randomising.
                # TODO: Stone should be a part of basemap to improve fps.
                random.seed(f"{entity.position}")
                plain_tile_index = 0
                sprite_num = random.randrange(
                    SPRITESHEET_DIMS["Stone"][plain_tile_index]
                )
                sprite_index = (plain_tile_index, sprite_num)
                random.seed()
            basemap.blit(
                sprite,
                coords_to_pixels(entity.position),
                get_sprite_box(*sprite_index),
            )
    return basemap


def pan_screen(
    current_frame: pygame.Surface,
    screen: pygame.surface.Surface,
    hud: Hud,
    old_center: tuple[int, int],
    new_center: tuple[int, int],
) -> None:
    """Smoothly pan the screen from old to new center

    TODO: Slide creatures from old_map position to new_map position (Warning: Hard)
    Best to keep move history in entities and read the new_map and most recent move.
    """
    speed = 5
    xdiff = int(new_center[0] - old_center[0])
    ydiff = int(new_center[1] - old_center[1])
    disp = get_disp(*old_center)
    for i in range(speed):
        xpos = int(disp[0] + xdiff * TSIZE * (i / speed))
        ypos = int(disp[1] + ydiff * TSIZE * (i / speed))
        screen.blit(current_frame, (0, 0), (xpos, ypos, disp[2], disp[3]))
        add_hud(screen, hud)
        pygame.display.flip()
        pygame.time.wait(20)


def adjust_step_volume(game: Game):
    # ToDo: implement max step amount instead of hard coding 25
    if not sound_system.muted:
        volume = 1 - (game.get_steps_remaining() / 25)
        sound_system.set_sound_volume("step", volume)


def play_death_animation(
    screen: pygame.surface.Surface,
    current_frame: pygame.surface.Surface,
    new_froglocation: tuple,
) -> None:
    # Player dead

    # This is incredibly ugly, needs rewrite.
    # Have text fade in, possibly have buttons unresponsive
    # for about 0.2 seconds so player doesn't skip death screen.
    # darken background (current_map) so it's clear you can't interact.
    # B&W filter instead of darken background?
    # Sound effect here would be great!
    magic_number = 0

    # plays croak sound upon death
    sound_system.play_sound("croak")

    while True:
        pygame.time.delay(50)
        you_died = font_render("You  Died", "Amatic-Bold.ttf", (130, 20, 60), 36 * 3)
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
        any_key = font_render(
            "(Press any key to continue)", "Amatic-Bold.ttf", (130, 20, 60), 25
        )
        any_key_pos = any_key.get_rect(
            centerx=screen.get_width() / 2,
            centery=screen.get_height() * 5 / 6,
        )

        white = pygame.Surface(screen.get_size())

        # Comment this out for a neat "bleary" death message.
        screen.blit(current_frame, (0, 0), get_disp(*new_froglocation))

        white.set_alpha(min((magic_number * 3 - 100), 200))
        screen.blit(white, (0, 0))
        you_died.set_alpha(magic_number * 5)
        screen.blit(you_died, you_died_pos)
        any_key.set_alpha(magic_number * 3 - 100)
        screen.blit(any_key, any_key_pos)
        pygame.display.flip()

        for event in pygame.event.get():
            process_universal_input(event)

            if magic_number > 20 and event.type == pygame.KEYDOWN:
                return

        magic_number += 1


def gui_loop(screen: pygame.surface.Surface) -> None:
    last_frame_time = pygame.time.get_ticks()
    now = pygame.time.get_ticks()
    game = Game()
    # Load the map. This will be a function when we have multiple maps to go between.
    hud = Hud()
    hud.update_element(
        "step_count",
        font_render(
            str(game.map.get_steps_left()), "Amatic-Bold.ttf", (130, 20, 60), 25
        ),
        (0, 0),
    )
    frog_location = game.get_player_pos()
    basemap = make_basemap(game.get_map().get_width(), game.get_map().get_height())
    map_changed = True
    frame_count = 0

    # Game loop
    while True:

        # Update game
        # Set max fps to 30 (33ms).
        if map_changed or (now := pygame.time.get_ticks()) - last_frame_time > 750:
            if BENCHMARK:
                benchmark.log_time_delta()
            last_frame_time = now
            frame_count += 1
            new_map = game.get_map()
            frame = draw_map(
                new_map.entities, copy(basemap), game.is_player_alive(), frame_count
            )
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
            process_universal_input(event)

            # If step made
            if process_event(event, game):
                adjust_step_volume(game)
                sound_system.play_sound("step")

                map_changed = True
                hud.update_element(
                    "step_count",
                    font_render(
                        str(game.map.get_steps_left()),
                        "Amatic-Bold.ttf",
                        (130, 20, 60),
                        25,
                    ),
                    (0, 0),
                )
                # Prevent skipping of movement animations
                break

    play_death_animation(screen, frame, new_froglocation)


def main() -> None:
    # Initialising stuff
    screen = pygame.display.set_mode(
        (WINDOW_TILE_WIDTH * TSIZE, WINDOW_TILE_HEIGHT * TSIZE),
        pygame.SCALED | pygame.RESIZABLE,
    )
    global SPRITESHEET_DIMS
    SPRITESHEET_DIMS = parse_assets(assets)
    while True:
        gui_loop(screen)

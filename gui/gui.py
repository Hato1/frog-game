"""Viewer/Controller model for Frog Game.

Controller:
    Accepts user input which is parsed to send to Frog Game.
Viewer:
    Shows a visual representation of the game state.

Height/Width refer to pixel values to be displayed.
Rows/Columns are coordinates in the game map/grid.
"""
import itertools
import math
import random
import time
from pathlib import Path

import pygame

from game.game import Game
from GAME_CONSTANTS import *
from gui.asset_loader import get_assets, get_spritesheet_dims
from gui.drawing import animate_step, draw_game
from gui.helper import Benchmark, font_render, get_sprite_box
from gui.hud import Hud
from gui.sound import SoundSystem
from gui.user_input import process_event, process_universal_input

# Enable to print frametimes to console.
# TODO: Make this a commandline argument
if BENCHMARK:
    benchmark = Benchmark()

pygame.init()

sound_system = SoundSystem()


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

    assets = get_assets()
    spritesheet_dims = get_spritesheet_dims()

    # TEMP: Default ground tile.
    default_map_tile = "Grass"
    # TEMP: Pad the map with this tile.
    default_padding_tile = "Stone"

    # TODO: Define these somewhere else. Named Tuple?
    plain_tile_index = 0
    particle_index = 11

    for x, y in itertools.product(range(padded_width), range(padded_height)):
        tile_name = (
            default_map_tile if point_in_map(x, y, map_width, map_height) else default_padding_tile
        )

        # Randomly choose which grass tile to draw
        rand_tile = random.randrange(spritesheet_dims[tile_name][plain_tile_index])
        basemap.blit(assets[tile_name], (x * TSIZE, y * TSIZE), get_sprite_box(col=rand_tile))

        # Randomly add fallen leaves
        thresh = 0.25
        while random.random() < thresh:
            rand_tile = random.randrange(spritesheet_dims["Tileset"][particle_index])
            basemap.blit(
                assets["Tileset"],
                (x * TSIZE, y * TSIZE),
                get_sprite_box(particle_index, rand_tile),
            )

            thresh /= 2
    return basemap


def adjust_step_volume(game: Game):
    # ToDo: implement max step amount instead of hard coding 25
    if not sound_system.muted:
        volume = 1 - (game.get_steps_remaining() / 25)
        sound_system.set_sound_volume("step", volume)


def play_death_animation(screen: pygame.surface.Surface) -> None:
    # Player dead

    # This is incredibly ugly, needs rewrite.
    # Have text fade in, possibly have buttons unresponsive
    # for about 0.2 seconds so player doesn't skip death screen.
    # darken background (current_map) so it's clear you can't interact.
    # B&W filter instead of darken background?
    magic_number = 0
    current_frame = screen.copy()

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
        any_key = font_render("(Press any key to continue)", "Amatic-Bold.ttf", (130, 20, 60), 25)
        any_key_pos = any_key.get_rect(
            centerx=screen.get_width() / 2,
            centery=screen.get_height() * 5 / 6,
        )

        white = pygame.Surface(screen.get_size())

        # Comment this out for a neat "bleary" death message.
        screen.blit(current_frame, (0, 0))

        white.set_alpha(min((magic_number * 3 - 100), 200))
        screen.blit(white, (0, 0))
        you_died.set_alpha(magic_number * 5)
        screen.blit(you_died, you_died_pos)
        any_key.set_alpha(magic_number * 3 - 100)
        screen.blit(any_key, any_key_pos)
        pygame.display.flip()

        for event in pygame.event.get():
            process_universal_input(event, sound_system)

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
        font_render(str(game.map.get_steps_left()), "Amatic-Bold.ttf", (130, 20, 60), 25),
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

            new_froglocation = game.get_player_pos()
            if ANIMATIONS and frog_location != new_froglocation:
                # pan_screen(frame, screen, hud, frog_location, new_froglocation)
                animate_step(
                    basemap,
                    screen,
                    hud,
                    new_map.entities,
                    frame_count,
                    10,
                )
            draw_game(
                basemap,
                screen,
                hud,
                new_map.entities,
                frame_count,
                game.is_player_alive(),
            )

            map_changed = False
            frog_location = new_froglocation
            if not game.is_player_alive():
                break

        # Process Input
        for event in pygame.event.get():
            process_universal_input(event, sound_system)

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

    play_death_animation(screen)


def main() -> None:
    # Initialising stuff
    screen = pygame.display.set_mode(
        (WINDOW_TILE_WIDTH * TSIZE, WINDOW_TILE_HEIGHT * TSIZE),
        pygame.SCALED | pygame.RESIZABLE,
    )
    while True:
        gui_loop(screen)

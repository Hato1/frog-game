"""Viewer/Controller model for Frog Game.

Controller: Parses user input and sends to game.
Viewer: Shows a visual representation of the game state.
"""
import pygame as pg

from game.game import Game
from GAME_CONSTANTS import *
from gui.death import play_death_animation
from gui.drawing import animate_step, draw_game
from gui.hud import hud
from gui.make_basemap import make_basemap
from gui.user_input import process_user_input

pg.init()


def play_game_loop(screen: pg.surface.Surface, clock: pg.time.Clock) -> None:
    game = Game()
    basemap = make_basemap(*game.get_map_dims())
    hud.update_step_counter(game.get_steps_left())
    drawing_stuff = (basemap, screen, clock, game.get_entities())
    map_changed = False

    while True:
        if ANIMATIONS and map_changed:
            animate_step(*drawing_stuff)
        draw_game(*drawing_stuff, draw_player=game.player_alive())

        if not game.player_alive():
            return

        # Process User Input
        map_changed = process_user_input(game)


def main() -> None:
    screen = pg.display.set_mode(
        (WINDOW_TILE_WIDTH * TSIZE, WINDOW_TILE_HEIGHT * TSIZE),
        pg.SCALED | pg.RESIZABLE,
    )
    clock = pg.time.Clock()
    while True:
        play_game_loop(screen, clock)
        play_death_animation(screen)

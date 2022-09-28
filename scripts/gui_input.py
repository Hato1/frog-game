import pygame as pg

from .game import Game
from .gui_helper import exit_game
from .helper import DOWN, LEFT, RIGHT, UP


def process_event(event: pg.event.Event, game: Game) -> bool:
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
    if event.type == pg.QUIT:
        exit_game()
    elif event.type == pg.KEYDOWN:
        match event.key:
            case pg.K_r:
                game.kill_player()

            case pg.K_w | pg.K_UP:
                return game.move(UP)
            case pg.K_a | pg.K_LEFT:
                return game.move(LEFT)
            case pg.K_s | pg.K_DOWN:
                return game.move(DOWN)
            case pg.K_d | pg.K_RIGHT:
                return game.move(RIGHT)
    return False


def process_universal_input(event: pg.event.Event, sound_system):
    """feed pygame events to allow the player to perform actions
    that aren't dependent on the players alive status"""
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_q:
            exit_game()

        elif event.key == pg.K_m:
            sound_system.toggle_mute()

        elif event.key == pg.K_p:
            sound_system.toggle_music()

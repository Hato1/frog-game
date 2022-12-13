import pygame as pg

from game.game import Game
from game.helper import DOWN, LEFT, RIGHT, UP
from gui.helper import exit_game
from gui.hud import hud
from gui.sound_system import sound_system


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
                game.kill_all()

            case pg.K_w | pg.K_UP:
                return game.move(UP)
            case pg.K_a | pg.K_LEFT:
                return game.move(LEFT)
            case pg.K_s | pg.K_DOWN:
                return game.move(DOWN)
            case pg.K_d | pg.K_RIGHT:
                return game.move(RIGHT)
            case pg.K_1:
                return game.force_change_world("map1")
            case pg.K_2:
                return game.force_change_world("map2")
            case pg.K_3:
                return game.force_change_world("map3")
            case pg.K_4:
                return game.force_change_world("map4")
            case pg.K_5:
                return game.force_change_world("map5")
            case pg.K_6:
                return game.force_change_world("map1.map")
    return False


def process_universal_input(event: pg.event.Event):
    """feed pygame events to allow the player to perform actions
    that aren't dependent on the players alive status"""
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_q:
            exit_game()

        elif event.key == pg.K_m:
            sound_system.toggle_mute()
            return True

        elif event.key == pg.K_p:
            sound_system.toggle_music()
            return True
    return False


def process_user_input(game):
    """Process valid user input when the game is active

    Returns:
        True if map has changed (Player took a step)
    """
    for event in pg.event.get():
        if process_universal_input(event):
            continue

        # If step made
        if process_event(event, game):
            sound_system.adjust_step_volume(game)
            sound_system.play_sound("step")

            hud.update_step_counter(game.get_steps_left())
            # Return early to prevent skipping of movement animations
            return True
    return False

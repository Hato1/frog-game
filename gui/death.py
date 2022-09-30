import math
import time

import pygame as pg

from gui.helper import font_render
from gui.sound_system import sound_system
from gui.user_input import process_universal_input


def play_death_animation(screen: pg.surface.Surface) -> None:
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
        pg.time.delay(50)
        you_died = font_render("You  Died", "Amatic-Bold.ttf", (130, 20, 60), 36 * 3)
        you_died = pg.transform.rotate(you_died, math.sin(time.time() / 1.5) * 10)
        you_died = pg.transform.scale(
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

        white = pg.Surface(screen.get_size())

        # Comment this out for a neat "bleary" death message.
        screen.blit(current_frame, (0, 0))

        white.set_alpha(min((magic_number * 3 - 100), 200))
        screen.blit(white, (0, 0))
        you_died.set_alpha(magic_number * 5)
        screen.blit(you_died, you_died_pos)
        any_key.set_alpha(magic_number * 3 - 100)
        screen.blit(any_key, any_key_pos)
        pg.display.flip()

        for event in pg.event.get():
            process_universal_input(event)

            if magic_number > 20 and event.type == pg.KEYDOWN:
                return

        magic_number += 1

from collections import namedtuple

import pygame as pg

from gui.helper import font_render


class Hud:
    HudElement = namedtuple("HudElement", "source dest")

    def __init__(self) -> None:
        self.elements: dict = {}

    def update_element(self, name: str, source: pg.surface.Surface, dest: tuple) -> None:
        """both adds and updates elements"""
        self.elements.update({name: self.HudElement(source, dest)})

    def get_elements(self) -> tuple:
        """returns a list to be used by blits"""
        return tuple((element.source, element.dest) for element in self.elements.values())

    @staticmethod
    def update_step_counter(steps_left):
        hud.update_element(
            "step_count",
            font_render(str(steps_left), "Amatic-Bold.ttf", (130, 20, 60), 25),
            (0, 0),
        )


def add_hud(screen: pg.surface.Surface) -> None:
    screen.blits(hud.get_elements())


hud = Hud()

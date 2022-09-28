from collections import namedtuple

import pygame as pg


class Hud:
    HudElement = namedtuple("HudElement", "source dest")

    def __init__(self) -> None:
        self.elements: dict = {}

    def update_element(
        self, name: str, source: pg.surface.Surface, dest: tuple
    ) -> None:
        """both adds and updates elements"""
        self.elements.update({name: self.HudElement(source, dest)})

    def get_elements(self) -> tuple:
        """returns a list to be used by blits"""
        return tuple(
            (element.source, element.dest) for element in self.elements.values()
        )


def add_hud(screen: pg.surface.Surface, hud: Hud) -> None:
    screen.blits(hud.get_elements())

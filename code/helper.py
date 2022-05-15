"""Various helper functions"""
from __future__ import annotations


def add_tuple(x: tuple, y: tuple) -> tuple:
    return tuple(x + y for x, y in zip(x, y))

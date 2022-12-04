"""Global module level variables to avoid circular imports."""
from typing import TYPE_CHECKING, Optional

from GAME_CONSTANTS import WORLD_NAME

if TYPE_CHECKING:
    from game.entity import Player
    from game.map import Map

worlds: dict[str, "Map"] = {}
current_world: Optional[str] = WORLD_NAME
player: Optional["Player"] = None


def __getattr__(name):
    if name == "world":
        return worlds[current_world]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

from pathlib import Path

from game.entity import *
from game.helper import Point
from gui.map_parser import get_dims, parse_entities_only


def new_entity_from_char(entity: str, point: Point) -> Optional[Entity]:
    match entity:
        case "P":
            return Player(
                "Player",
                position=point,
                tags=[Tags.hops, Tags.pusher, Tags.player],
            )
        case "F":
            return NormalNorman(
                "FrogR",
                position=point,
                tags=[Tags.hops, Tags.kills_player, Tags.pusher],
            )
        case "G":
            return NormalNorman("FrogR", position=point, tags=[Tags.hops, Tags.kills_player, Tags.pusher], state=3)
        case "B":
            return BarrelingBarrel(
                "Barrel",
                position=point,
                tags=[Tags.pushable, Tags.barrel],
            )
        case "W":
            return Wall("rockwall", position=point, tags=[Tags.solid, Tags.no_animation])
        case "O":
            return Stone("Stone", position=point, tags=[Tags.solid, Tags.no_animation])
        case "S":
            return SpiralingStacy(
                "FrogY",
                position=point,
                tags=[Tags.hops, Tags.kills_player, Tags.pusher],
            )
        case "T":
            return TrickyTrent(
                "FrogP",
                position=point,
                tags=[Tags.hops, Tags.kills_player, Tags.pusher],
            )
        case "L":
            return SlidingStone(
                "SlidingStone",
                position=point,
                tags=[Tags.pushable, Tags.no_animation],
            )
    return None


def populate_entity_list(map_file: Path) -> tuple[list[Entity], Player, Point]:
    """Read entities from a map file and insert them into the entity list"""
    player: Optional[Player] = None
    if map_file.suffix == ".map":
        entities = parse_entities_only(map_file)
        for e in entities:
            if type(e) == Player:
                assert not player
                player = e
        assert player
        return entities, player, get_dims(map_file)

    entities = []
    with open(map_file) as file:
        y = 0
        max_x = 0
        for line in file:
            x = 0
            line = line.strip()
            if set(line) == {"-"}:
                continue
            for char in line:
                if char in ["|", "-"]:
                    continue
                if entity := new_entity_from_char(char, Point(x, y)):
                    if type(entity) == Player:
                        assert not player
                        player = entity
                    entities.append(entity)
                x += 1
                max_x = max(x, max_x)
            y += 1
    return entities, player, Point(max_x, y)

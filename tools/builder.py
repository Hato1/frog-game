# mypy: ignore-errors
"""Map Builder Tool"""

import contextlib
import pickle
from copy import deepcopy
from itertools import product, repeat
from json import load
from math import ceil, floor
from random import randint
from time import perf_counter, sleep, time
from typing import List
from warnings import warn

import pygame as pg

# from scripts.entity import Creature, Entity
from gui.asset_loader import get_spritesheet_dims

Config = {
    "Width": 16,  # number of tiles wide the screen is (make adjustable in the future)
    "Height": 8,  # number of high wide the screen is (make adjustable in the future)
    "WindowScale": 3,  # zoom to calculate window size at (would be better to make adjustable)
    "Zoom": 2,  # default zoom level of the screen
    "CamPos": [0, 0],  # staring (top left) camera position
    "SpriteRes": 25,  # resolution single tile sprites (1x1)
    "Debounce": 1000,
    "Fps": 15,  # set refresh rate cap
    "SaveDelay": 0.5,  # Save wait time (in seconds)
    "SelectedTile": "Dirt",  # initial selected tile
}

# Declare Global variables
NewRes = Config["SpriteRes"] * Config["WindowScale"]
SaveCycles = floor(Config["Fps"] * Config["SaveDelay"])
ActionFlag = True
SaveCounter = SaveCycles + 1
MouseDown = False
SelectedTile = Config["SelectedTile"]
ClickDown = 0, 0
ScreenSurf = [pg.Surface((0, 0)), pg.Surface((0, 0))]
Redraw = False
CamPos = Config["CamPos"]
Zoom = Config["Zoom"]
debounce = Config["Debounce"]

# select which map to edit
FileName = "map1"


class Asset:
    def __init__(self, name: str, num_sprites: list[int], sprite_row: int):
        self.name = name
        self.sprite_row = sprite_row
        self.num_sprites = num_sprites
        self.sprite_col = 0
        self.hue_adjust = 0
        self.sprite_path = ""

    def create_sprite_path(self):
        self.sprite_path = f"assets/{self.name}.png"


class Tile(Asset):
    def __init__(
        self,
        name: str,
        num_sprites: list[int],
        sprite_col: int,
        level: int,
        sprite_row=None,
        hue_adjust=None,
        sprite_path=None,
    ):
        super().__init__(name, num_sprites, 0)
        self.sprite_row = sprite_row or randint(0, num_sprites[sprite_col] - 1)
        self.sprite_col = sprite_col
        self.num_sprites = num_sprites
        self.level = level
        self.hue_adjust = hue_adjust
        self.sprite_path = sprite_path or f"assets/{self.name}.png"

    def randomise_tile(self):
        """re-randomise the sprite row"""
        self.sprite_row = randint(0, self.num_sprites[self.sprite_col] - 1)


class Entity(Asset):
    def __init__(
        self,
        name: str,
        num_sprites: list[int],
        tags: [str],
        sprite_names: [[str]],
        direction=None,
        sprite_row=None,
        sprite_col=None,
        hue_adjust=None,
        sprite_path=None
    ):
        super().__init__(name, num_sprites, 0)
        self.direction = direction or ["Up", "Left", "Right", "Down"][0]
        self.tags = tags
        self.sprite_names = sprite_names
        self.hue_adjust = hue_adjust
        self.sprite_path = sprite_path or f"assets/{self.name}.png"

    # sprites = loop over sprite names and make (x, y, 25, 25)


Background_Data = [[[]]]
Foreground_Data = [[[]]]


def resize_map_data(list_list: list[list], dimensions: [int], default_object: Asset) -> list:
    """take a list of lists and expand to match dimensions while including default_object."""
    diff_col = dimensions[1] - len(list_list)
    if diff_col < 0:
        list_list = list_list[:diff_col]
    if diff_col > 0:
        for _ in range(diff_col):
            list_list.append([])

    for row in list_list:
        diff_row = dimensions[0] - len(row)
        if diff_row < 0:
            del row[dimensions[0]:]
        if diff_row > 0:
            for _ in range(diff_row):
                row.extend([[default_object]])
    return list_list


def conv_list_dict(list_of_dicts: [dict], name_key: str) -> dict:
    """takes a list of dictionary's and returns a dictionary of dictionaries"""
    return {dictionary[name_key]: dictionary for dictionary in list_of_dicts}


def add_dict_surf(encyclopedia: dict, file_key: str, path: str) -> dict:
    """Adds a surface to each dict in the encyclopedia based on the file referenced in the same dictionary."""
    for dic in encyclopedia:
        encyclopedia[dic]["Surface"] = amend_transparent(
            pg.image.load(path + encyclopedia[dic][file_key])
        )
    return encyclopedia


def add_dict_obj(encyclopedia: dict, any_object: any, key: str) -> dict:
    """Adds an entry to each dict in an encyclopedia."""
    for dic in encyclopedia:
        encyclopedia[dic][key] = any_object
    return encyclopedia


def add_surface_dims(encyclopedia: dict) -> dict:
    """take the surfaces in the encyclopedia and returns the encyclopedia with a dimensions entry"""
    # surface_dict = {dic: encyclopedia[dic]["Surface"] for dic in encyclopedia}
    image_dims = get_spritesheet_dims()  # surface_dict)
    for dic in encyclopedia:
        encyclopedia[dic]["dims"] = image_dims[dic]
    return encyclopedia


def load_dicts(meta_data_file, list_key: str, name_key: str, tile_type: str) -> dict:
    """take a list of dicts do thing to make format correct for the loops."""
    encyclopedia = conv_list_dict(meta_data_file[list_key], name_key)

    encyclopedia = add_dict_surf(encyclopedia, "FileName", "assets/")

    encyclopedia = add_dict_obj(encyclopedia, tile_type, "Type")

    encyclopedia = add_surface_dims(encyclopedia)

    return encyclopedia


def amend_transparent(surf: pg.Surface) -> pg.Surface:
    """if a tile is transparent replace it with a red cross."""
    alpha = pg.transform.average_color(surf.convert_alpha())
    if alpha[-1] == 0:
        surf = pg.image.load("assets/TransparentME.png")
    return surf


def cell_interpreter(cell: list[Asset], encyclopedia: dict) -> list:
    """given a cell, returns list of sprites to blit."""
    return [encyclopedia[obj.name]["Surface"] for obj in cell]


def draw_screen(
    back_screen: pg.Surface,
    fore_screen: pg.Surface,
    window: pg.surface.Surface,
    encyclopedia: dict,
) -> None:
    """blit all elements on screen."""
    # Draw a grey rectangle over the screen to blank
    pg.draw.rect(
        window,
        (20, 20, 20),
        pg.Rect(
            0,
            0,
            Config["Width"] * Config["SpriteRes"] * Config["WindowScale"],
            (Config["Height"] + 1) * Config["SpriteRes"] * Config["WindowScale"],
        ),
    )

    # loop over every tile on display in the map and blit sprite
    window.blit(back_screen, (0, 0))
    window.blit(fore_screen, (0, 0))

    # Draw a black rectangle for options to sit on
    pg.draw.rect(
        window,
        (0, 0, 0),
        pg.Rect(
            Config["SpriteRes"] - 2,
            Config["Height"] * NewRes + Config["SpriteRes"] - 2,
            Config["Width"] * NewRes - Config["SpriteRes"] * 2 - 14,
            Config["SpriteRes"] + 4,
        ),
    )

    # Draw a white rectangle for the currently selected sprite
    index = list(encyclopedia).index(SelectedTile)
    pg.draw.rect(
        window,
        (255, 255, 255),
        pg.Rect(
            (((Config["SpriteRes"] + 2) * index) + Config["SpriteRes"] - 2),
            (Config["Height"] * NewRes) + Config["SpriteRes"] - 2,
            Config["SpriteRes"] + 4,
            Config["SpriteRes"] + 4,
        ),
    )

    draw_buttons(encyclopedia, window)


def flip_display(encyclopedia: dict, window: pg.surface.Surface) -> List[pg.surface.Surface]:
    """take data and draw it to the display"""
    background_map = [
        [cell_interpreter(cell, encyclopedia) for cell in row1] for row1 in Background_Data
    ]
    foreground_map = [
        [cell_interpreter(cell, encyclopedia) for cell in row1] for row1 in Foreground_Data
    ]
    back_surface = create_map_surface(
        background_map, Background_Data, CamPos, Zoom
    )  # [1] = top, [0] = left
    fore_surface = create_map_surface(foreground_map, Foreground_Data, CamPos, Zoom)

    draw_screen(back_surface, fore_surface, window, encyclopedia)

    pg.display.flip()
    return [back_surface, fore_surface]


def draw_buttons(encyclopedia: dict, window: pg.surface.Surface) -> None:
    """Place selectable options for each entry in the encyclopedia."""
    for surface_index, surf in enumerate(encyclopedia):
        window.blit(
            encyclopedia[surf]["Surface"],
            (
                (surface_index * 1.09) * Config["SpriteRes"] + Config["SpriteRes"],
                NewRes * Config["Height"] + Config["SpriteRes"],
            ),
            (0, 0, Config["SpriteRes"], Config["SpriteRes"]),
        )


def blit_assets(
    map_surf: pg.Surface,
    surfs_at_point: list[pg.Surface],
    assets_at_point: list[Asset],
    point: tuple,
    zoom: int,
) -> pg.Surface:
    for ind, surf in enumerate(surfs_at_point):
        w, h = surf.get_size()
        map_surf.blit(
            pg.transform.scale(surf, (zoom * w, zoom * h)),
            (
                point[0] * Config["SpriteRes"] * zoom,
                point[1] * Config["SpriteRes"] * zoom,
            ),
            (
                assets_at_point[ind].sprite_col * Config["SpriteRes"] * zoom,
                assets_at_point[ind].sprite_row * Config["SpriteRes"] * zoom,
                Config["SpriteRes"] * zoom,
                Config["SpriteRes"] * zoom,
            ),
        )
    return map_surf


def draw_grid(map_surf: pg.Surface, point: tuple, zoom: int):
    pg.draw.rect(
        map_surf,
        (0, 0, 0),
        pg.Rect(
            point[0] * Config["SpriteRes"] * zoom,
            point[1] * Config["SpriteRes"] * zoom,
            Config["SpriteRes"] * zoom,
            Config["SpriteRes"] * zoom,
        ),
        1,
    )
    return map_surf


def create_map_surface(
    map_list: list, tile_list: list, display_origin: [int], zoom: int
) -> pg.Surface:
    """loop over every tile on display and create a surface of the map."""

    # define map surface size and transparency settings
    map_surf = pg.Surface(
        (Config["Width"] * NewRes, Config["Height"] * NewRes + NewRes), pg.SRCALPHA
    )

    # figure out what tiles to evaluate
    num_rows_on_display = ceil(Config["Width"] * (Config["WindowScale"] / zoom))
    num_cols_on_display = ceil(1 + Config["WindowScale"] - Zoom) + ceil(
        Config["Height"] * (Config["WindowScale"] / zoom)
    )

    last_valid_row_on_display = min(num_rows_on_display, len(map_list[0]) - display_origin[0])
    last_valid_col_on_display = min(num_cols_on_display, len(map_list) - display_origin[1])

    first_valid_row_on_display = max(0, 0 - display_origin[0])
    first_valid_col_on_display = max(0, 0 - display_origin[1])

    rows_to_evaluate = range(first_valid_row_on_display, last_valid_row_on_display)
    cols_to_evaluate = range(first_valid_col_on_display, last_valid_col_on_display)

    # for each row column to evaluate blit sprite
    for row, col in product(rows_to_evaluate, cols_to_evaluate):
        surfs_at_point: List[pg.Surface] = map_list[(col + display_origin[1])][
            (row + display_origin[0])
        ]
        assets_at_point: List[Asset] = tile_list[(col + display_origin[1])][
            (row + display_origin[0])
        ]

        map_surf: pg.Surface = blit_assets(
            map_surf, surfs_at_point, assets_at_point, (row, col), zoom
        )

        map_surf = draw_grid(map_surf, (row, col), zoom)

    return map_surf


def select_tile(click: tuple[int, int], dictionary) -> str:
    """returns the key of the clicked selectable."""
    index = floor(click[0] / (Config["SpriteRes"] + 2) - 1)
    return list(dictionary)[index]


def clicked_index(click: tuple, campos: list, meta_data: dict) -> tuple:
    """return the row and column of the clicked tile."""
    index = [
        (floor(coord / (Config["SpriteRes"] * Zoom)) + campos[i]) % meta_data["MapSize"][i]
        for i, coord in enumerate(click)
    ]

    return tuple(index)


def write_map_pickle(dat: list) -> None:
    """Save the map file to a pickle."""
    with open("maps/map1.map", "wb") as file:
        pickle.dump(dat, file)


def apply_selected(cell_list: list, tile: Asset, tile_type: str) -> list:
    """Take the current selected tile object and paint to map."""
    match tile_type:
        case "Tile":
            cell_list = [tile]
        case "Ent":
            tile = tile
            cell_list.append(tile)
        case _:
            warn("Tile type not expected")

    return cell_list


def draw_box(window: pg.surface.Surface, encyclopedia: dict) -> None:
    """drawer the selection box when dragging."""
    global ScreenSurf
    global ClickDown

    mouse_position = pg.mouse.get_pos()
    draw_screen(ScreenSurf[0], ScreenSurf[1], window, encyclopedia)
    pg.draw.rect(
        window,
        (255, 255, 255),
        pg.Rect(
            min(ClickDown[0], mouse_position[0]),
            min(ClickDown[1], mouse_position[1]),
            abs(mouse_position[0] - ClickDown[0]),
            abs(mouse_position[1] - ClickDown[1]),
        ),
        2,
    )
    pg.display.flip()


def fps_limiter(start: float) -> None:
    """Sleeps in order to maintain a constant FPS."""
    runtime = perf_counter() - start
    # print(1/runtime)
    if runtime > (1 / Config["Fps"]):
        runtime = 0
    sleep((1 / Config["Fps"]) - runtime)


def move_camera(event_key: pg.event.Event) -> None:
    """Change camera position index when passed a keypress"""
    global CamPos
    match event_key:
        case pg.K_UP:
            CamPos[1] = CamPos[1] - 1
        case pg.K_DOWN:
            CamPos[1] = CamPos[1] + 1
        case pg.K_LEFT:
            CamPos[0] = CamPos[0] - 1
        case pg.K_RIGHT:
            CamPos[0] = CamPos[0] + 1


def apply_paired_ent(encyclopedia: dict, row: int, col: int):
    """when placing tiles place an entity on the same location as the tile, otherwise remove all entities"""
    tile: Tile = Background_Data[row][col][0]
    Foreground_Data[row][col] = []
    paired_ent = encyclopedia[tile.name]["PairedEntity"]
    if paired_ent != 0:
        apply_selected(
            Foreground_Data[row][col],
            Entity(
                encyclopedia[paired_ent]["Name"],
                encyclopedia[paired_ent]["dims"],
                encyclopedia[paired_ent]["Tags"],
                encyclopedia[paired_ent]["SpriteNames"],
            ),
            "Ent",
        )


def are_match(tile_level: int, corners: (), sides: ()) -> tuple[list[bool], list[bool]]:
    """checks if sides and corners are of the same or greater level then the current tile"""
    corner_match = [False, False, False, False]
    side_match = [False, False, False, False]

    for index, corner in enumerate(corners):
        if corner >= tile_level:
            corner_match[index] = True

    for index, side in enumerate(sides):
        if side >= tile_level:
            side_match[index] = True

    return corner_match, side_match


def determine_edge_case(corner_matches: [bool], side_matches: [bool]) -> tuple[int, int]:
    """determine based on the surrounding tiles levels what sprite column a tile it should be"""
    """first number is the index of the tile second number is where to get the under-piece from"""

    # location key:
    # 1 2 3
    # 4   5
    # 6 7 8

    matches = sum(corner_matches + side_matches)
    match matches:
        case 3:
            match corner_matches:
                case True, False, False, False:
                    return 9, 6  # bottom left
                case False, True, False, False:
                    return 11, 1  # top left
                case False, False, True, False:
                    return 12, 3  # top right
                case False, False, False, True:
                    return 10, 8  # bottom right

        case 4:
            match side_matches:
                case True, True, False, False:
                    return 11, 1  # top left
                case False, True, True, False:
                    return 9, 6  # bottom left
                case False, False, True, True:
                    return 10, 8  # bottom right
                case True, False, False, True:
                    return 12, 3  # top right

        case 5:
            match corner_matches:
                case True, True, False, False:
                    return 1, 4  # left
                case False, True, True, False:
                    return 4, 2  # top
                case False, False, True, True:
                    return 2, 5  # right
                case True, False, False, True:
                    return 3, 7  # bottom

            match side_matches:
                case True, True, False, False:
                    return 11, 1  # top left
                case False, True, True, False:
                    return 9, 6  # bottom left
                case False, False, True, True:
                    return 10, 8  # bottom right
                case True, False, False, True:
                    return 12, 3  # top right

        case 6:
            match side_matches:
                case True, True, True, False:
                    return 1, 4  # left
                case False, True, True, True:
                    return 3, 7  # bottom
                case True, False, True, True:
                    return 2, 5  # right
                case True, True, False, True:
                    return 4, 2  # top

        case 7:
            match corner_matches:
                case True, True, True, False:
                    return 7, 1  # inset top left
                case False, True, True, True:
                    return 8, 3  # inset top right
                case True, False, True, True:
                    return 6, 8  # inset bottom right
                case True, True, False, True:
                    return 5, 6  # inset bottom left

            match side_matches:
                case True, True, True, False:
                    return 1, 4  # left
                case False, True, True, True:
                    return 3, 7  # bottom
                case True, False, True, True:
                    return 2, 5  # right
                case True, True, False, True:
                    return 4, 2  # top

    return 0, 0


def add_outer_ring(tile_map: list[list[list]]) -> list[list[list]]:
    """creates a new tile map width extra row of level 3 tiles on all sides"""
    temp_map = deepcopy(tile_map)

    for row in temp_map:
        row.insert(0, [Tile("TEMP", [1], 0, 3)])
        row.append([Tile("TEMP", [1], 0, 3)])
    temp_map.insert(0, list(repeat([Tile("TEMP", [1], 0, 3)], len(temp_map[0]))))
    temp_map.append(list(repeat([Tile("TEMP", [1], 0, 3)], len(temp_map[0]))))

    return temp_map


def determine_background_type(location: int, row: int, col: int) -> str:
    # location key:
    # 1 2 3
    # 4   5
    # 6 7 8

    match location:
        case 1:
            return Background_Data[row - 1][col - 1][-1].name
        case 2:
            return Background_Data[row - 1][col][-1].name
        case 3:
            return Background_Data[row - 1][col + 1][-1].name
        case 4:
            return Background_Data[row][col - 1][-1].name
        case 5:
            return Background_Data[row][col + 1][-1].name
        case 6:
            return Background_Data[row + 1][col - 1][-1].name
        case 7:
            return Background_Data[row + 1][col][-1].name
        case 8:
            return Background_Data[row + 1][col + 1][-1].name
    return "Grass"


def apply_edges(row: int, col: int) -> None:
    """given row and col change the sprite column"""
    current_tile = Background_Data[row][col][-1]
    tile_type = current_tile.level

    temp_map = add_outer_ring(Background_Data)

    row += 1
    col += 1

    corners = (
        temp_map[row - 1][col + 1][-1].level,
        temp_map[row + 1][col + 1][-1].level,
        temp_map[row + 1][col - 1][-1].level,
        temp_map[row - 1][col - 1][-1].level,
    )  # clockwise starting top left
    sides = (
        temp_map[row + 1][col][-1].level,
        temp_map[row][col + 1][-1].level,
        temp_map[row - 1][col][-1].level,
        temp_map[row][col - 1][-1].level,
    )  # clockwise starting top

    row -= 1
    col -= 1

    corner_match, side_match = are_match(tile_type, corners, sides)
    index = determine_edge_case(corner_match, side_match)

    Background_Data[row][col][-1] = Tile(
        current_tile.name, current_tile.num_sprites, index[0], current_tile.level
    )

    tile_name = determine_background_type(index[1], row, col)

    Background_Data[row][col] = [Tile(tile_name, current_tile.num_sprites, 0, 1)] + [
        Background_Data[row][col][-1]
    ]


def apply_tile(meta: dict, click_up: tuple, encyclopedia: dict) -> None:
    """add the selected Asset to the Map"""
    index_down = clicked_index(ClickDown, CamPos, meta)
    index_up = clicked_index(click_up, CamPos, meta)

    rows = index_up[1] - index_down[1]
    cols = index_up[0] - index_down[0]

    row_sign = -1 if rows < 0 else 1
    rows = abs(rows) + 1
    col_sign = -1 if cols < 0 else 1
    cols = abs(cols) + 1

    for row, col in product(range(rows), range(cols)):
        match encyclopedia[SelectedTile]["Type"]:
            case "Tile":
                selected_asset = Tile(
                    encyclopedia[SelectedTile]["Name"],
                    encyclopedia[SelectedTile]["dims"],
                    0,
                    encyclopedia[SelectedTile]["level"],
                )
            case "Ent":
                selected_asset = Entity(
                    encyclopedia[SelectedTile]["Name"],
                    encyclopedia[SelectedTile]["dims"],
                    encyclopedia[SelectedTile]["Tags"],
                    encyclopedia[SelectedTile]["SpriteNames"],
                )
            case _:
                warn("No asset type found")
                selected_asset = []

        the_map = apply_selected(
            Background_Data[index_down[1] + row * row_sign][index_down[0] + col * col_sign],
            selected_asset,
            encyclopedia[SelectedTile]["Type"],
        )

        Background_Data[index_down[1] + row * row_sign][index_down[0] + col * col_sign] = the_map

        apply_paired_ent(
            encyclopedia, index_down[1] + row * row_sign, index_down[0] + col * col_sign
        )

    for row, col in product(range(rows + 2), range(cols + 2)):
        with contextlib.suppress(IndexError):
            apply_edges(
                index_down[1] - row_sign + row * row_sign,
                index_down[0] - col_sign + col * col_sign,
            )


def convert_classes_to_dicts(background: [[Tile]], foreground: [[Entity]]) -> []:
    """takes the maps and coverts class objects to dicts to be saved"""
    for i, row in enumerate(background):
        for j, col in enumerate(row):
            for k, item in enumerate(col):
                background[i][j][k] = item.__dict__

    for i, row in enumerate(foreground):
        for j, col in enumerate(row):
            for k, item in enumerate(col):
                foreground[i][j][k] = item.__dict__

    return [background, foreground]


def event_handler(window: pg.surface.Surface, encyclopedia: dict, meta: dict) -> None:
    """takes pygame event and calls actions."""
    global Zoom, SelectedTile, ClickDown
    global MouseDown, ScreenSurf, ActionFlag
    global SaveCounter, Redraw, debounce
    global Background_Data, Foreground_Data

    # handle pygame events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit(0)

        match event.type:
            case pg.KEYDOWN:
                Redraw = True
                move_camera(event.key)

            case pg.MOUSEBUTTONDOWN:
                # on left click
                if event.button == pg.BUTTON_LEFT:
                    MouseDown = True
                    Redraw = True
                    ClickDown = pg.mouse.get_pos()

                    # If clicking on editable area apply currently selected entity
                    if (
                        ClickDown[1] < Config["Height"] * NewRes
                        and encyclopedia[SelectedTile]["Type"] == "Ent"
                    ):
                        ActionFlag = False  # reset the save timer
                        pg.display.set_caption(f"Frog game editor{FileName} (Unsaved)")
                        ind = clicked_index(ClickDown, CamPos, meta)
                        Foreground_Data[ind[1]][ind[0]] = apply_selected(
                            Foreground_Data[ind[1]][ind[0]],
                            Entity(
                                encyclopedia[SelectedTile]["Name"],
                                encyclopedia[SelectedTile]["dims"],
                                encyclopedia[SelectedTile]["Tags"],
                                encyclopedia[SelectedTile]["SpriteNames"],
                            ),
                            encyclopedia[SelectedTile]["Type"],
                        )

                    # If clicking on tile selection area change paintbrush tile
                    if (
                        Config["Height"] * NewRes + Config["SpriteRes"]
                        < ClickDown[1]
                        < Config["Height"] * NewRes + (2 * Config["SpriteRes"])
                    ):
                        SelectedTile = select_tile(ClickDown, encyclopedia)

                # on right click delete top entity
                if event.button == pg.BUTTON_RIGHT:
                    ClickDown = pg.mouse.get_pos()

                    # Remove top entity if it exists
                    if ClickDown[1] < Config["Height"] * NewRes:
                        ind = clicked_index(ClickDown, CamPos, meta)

                        ActionFlag = False  # reset the save timer
                        Redraw = True
                        pg.display.set_caption(f"Frog game editor{FileName} (Unsaved)")
                        Foreground_Data[ind[1]][ind[0]] = Foreground_Data[ind[1]][ind[0]][:-1]

            # if click_up with background tile type selected do a drag
            case pg.MOUSEBUTTONUP:
                MouseDown = False
                if encyclopedia[SelectedTile]["Type"] == "Tile" and event.button == pg.BUTTON_LEFT:
                    click_up = pg.mouse.get_pos()
                    if click_up[1] < Config["Height"] * NewRes > ClickDown[1]:
                        Redraw = True
                        ActionFlag = False  # reset the save timer
                        pg.display.set_caption(f"Frog game editor{FileName} (Unsaved)")

                        apply_tile(meta, click_up, encyclopedia)

            # on scroll zoom
            case pg.MOUSEWHEEL:
                if int(round(time() * 1000)) > debounce:
                    Redraw = True
                    debounce = int(round(time() * Config["Debounce"])) + 150
                    Zoom = Zoom + event.y
                    Zoom = max(Zoom, 1)
                    Zoom = Config["WindowScale"] if Zoom > Config["WindowScale"] else Zoom

        # redraw map now button has been released
        if Redraw:
            ScreenSurf = flip_display(encyclopedia, window)
            Redraw = False

    # if mouse state is down draw box of selection
    if MouseDown and encyclopedia[SelectedTile]["Type"] == "Tile":
        draw_box(window, encyclopedia)

    # Save map to pickle file
    if ActionFlag is False:  # If an action occurs
        SaveCounter = 0  # Reset save delay
        ActionFlag = True  # Reset action flag to true

    SaveCounter += 1  # Increment counter eah time the code runs

    # Once save delay is met save the file
    if SaveCounter == SaveCycles:
        converted = convert_classes_to_dicts(deepcopy(Background_Data), deepcopy(Foreground_Data))
        write_map_pickle(converted)
        pg.display.set_caption(f"Frog game editor{FileName} (Saved)")


def randomise_tiles(background: [[[Tile]]]):
    """run through all tiles on the map and randomise their sprite index"""
    for row in background:
        for col in row:
            for tile in col:
                tile.randomise_tile()
    return background


def convert_dicts_to_classes(background: [[[{}]]], foreground: [[[{}]]]):
    """takes the maps and coverts dict objects to classes to be used"""
    for i, row in enumerate(background):
        for j, col in enumerate(row):
            for k, item in enumerate(col):
                background[i][j][k] = Tile(**item)

    for i, row in enumerate(foreground):
        for j, col in enumerate(row):
            for k, item in enumerate(col):
                foreground[i][j][k] = Entity(**item)

    return background, foreground


def load_save(meta_data: any, encyclopedia: dict) -> tuple[list, list]:
    """load map pickle and resize to match config file"""
    try:
        with open(f"maps/{FileName}.map", "rb") as MapFile:
            data: List[list] = pickle.load(MapFile)
            background = data[0]
            foreground = data[1]
    except (FileNotFoundError, NameError):
        background = []
        foreground = []

    background, foreground = convert_dicts_to_classes(background, foreground)

    # import map dimensions from metadata file
    map_dimensions: List[int] = meta_data["MapSize"]

    background = resize_map_data(
        background,
        map_dimensions,
        Tile("Stone", encyclopedia["Stone"]["dims"], 0, encyclopedia["Stone"]["level"]),
    )
    background = randomise_tiles(background)
    foreground = resize_map_data(
        foreground,
        map_dimensions,
        Entity(
            "InvisWall",
            encyclopedia["InvisWall"]["dims"],
            encyclopedia["InvisWall"]["Tags"],
            encyclopedia["InvisWall"]["SpriteNames"],
        ),
    )
    return background, foreground


def main() -> None:
    global Background_Data, Foreground_Data, ScreenSurf
    with open(f"maps/{FileName}.json") as metadata_file:
        metadata = load(metadata_file)

    window = pg.display.set_mode(
        (Config["Width"] * NewRes, Config["Height"] * NewRes + NewRes)
    )  # set display size

    # load in dicts
    encyclopedia = load_dicts(metadata, "Tiles", "Name", "Tile")
    encyclopedia.update(load_dicts(metadata, "Entities", "Name", "Ent"))

    Background_Data, Foreground_Data = load_save(metadata, encyclopedia)

    Background_Data = randomise_tiles(Background_Data)

    pg.display.set_caption(f"Frog game editor{FileName}")

    ScreenSurf = flip_display(encyclopedia, window)

    # loop that runs event_handler at specific rate
    while True:
        t1_start = perf_counter()

        event_handler(window, encyclopedia, metadata)

        fps_limiter(t1_start)


main()

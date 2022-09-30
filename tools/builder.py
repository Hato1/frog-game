# mypy: ignore-errors
"""Map Builder Tool"""


import itertools
import pickle
from json import load
from math import ceil, floor
from time import perf_counter, sleep, time
from typing import List
from warnings import warn

import pygame as pg

# from scripts.entity import Creature, Entity

Config = {
    "Width": 16,  # number of tiles wide the screen is (make adjustable in the future)
    "Height": 9,  # number of high wide the screen is (make adjustable in the future)
    "WindowScale": 3,  # zoom to calculate window size at (would be better to make adjustable)
    "Zoom": 2,  # default zoom level of the screen
    "CamPos": [0, 0],  # staring (top left) camera position
    "SpriteRes": 25,  # resolution single tile sprites (1x1)
    "Debounce": 1000,
    "Fps": 15,  # set refresh rate cap
    "SaveDelay": 1,  # Save wait time (in secodns)
    "SelectedTile": "Dirt",  # inital selected tile
}

# Declare Global variables
NewRes = Config["SpriteRes"] * Config["WindowScale"]
SaveCycles = floor(Config["Fps"] * Config["SaveDelay"])
ActionFlag = True
SaveCounter = SaveCycles + 1
MouseDown = False
SelectedTile = Config["SelectedTile"]
ClickDown = 0, 0
ScreenSurf = pg.Surface((0, 0))
Redraw = False
CamPos = Config["CamPos"]
Zoom = Config["Zoom"]
debounce = Config["Debounce"]
Background_Data = []
Foreground_Data = []

# select which map to edit
FileName = "map1"


def resize_map_data(data: [list], dimentions: [int], default_object: any) -> list:
    """take a list of lists and expand to match dimentions while including default_object."""
    diff_col = dimentions[1] - len(data)
    if diff_col < 0:
        data = data[:diff_col]
    if diff_col > 0:
        for _ in range(diff_col):
            data.append([])

    for row in data:
        diff_row = dimentions[0] - len(row)
        if diff_row < 0:
            row = row[:diff_row]
        if diff_row > 0:
            for _ in range(diff_row):
                row.extend([[default_object]])
    return data


def conv_list_dict(list_of_dicts: [dict], name_key: str) -> dict:
    """takes a list of dictionarys and returns a dicitionary of dicitonaries"""
    return {dictionary[name_key]: dictionary for dictionary in list_of_dicts}


def add_dict_surf(encyclopedia: dict, file_key: str, path: str) -> dict:
    """Adds a surface to each dict in the encyclopedia based on the file refernced in the same dictionary."""
    for dic in encyclopedia:
        encyclopedia[dic]["Surface"] = amend_transparent(
            pg.image.load(path + encyclopedia[dic][file_key])
        )
    return encyclopedia


def add_dict_str(encyclopedia: dict, string: any, key: str) -> dict:
    """Adds an entry to each dict in an encyclopedia."""
    for dic in encyclopedia:
        encyclopedia[dic][key] = string
    return encyclopedia


def load_dicts(meta_data_file, tiles_key: str, ents_key: str) -> dict:
    tile_dictionarys = conv_list_dict(meta_data_file[tiles_key], "level")
    ent_dictionarys = conv_list_dict(meta_data_file[ents_key], "Name")

    tile_dictionarys = add_dict_surf(tile_dictionarys, "FileName", "../assets/")
    ent_dictionarys = add_dict_surf(ent_dictionarys, "FileName", "../assets/")

    tile_dictionarys = add_dict_str(tile_dictionarys, "Tile", "Type")
    ent_dictionarys = add_dict_str(ent_dictionarys, "Ent", "Type")

    tile_dictionarys.update(ent_dictionarys)

    return tile_dictionarys


def amend_transparent(surf: pg.Surface) -> pg.Surface:
    """if a tile is tranparent replace it with a red cross."""
    alpha = pg.transform.average_color(surf.convert_alpha())
    if alpha[-1] == 0:
        surf = pg.image.load("../assets/TransparentME.png")
    return surf


def cellinterp(encyclopedia: dict, cell: list, key: str) -> list:
    """given a cell, returns list of sprites to blit."""
    return [encyclopedia[obj][key] for obj in cell]


def drawscreen(
    screen: pg.Surface, window: pg.surface.Surface, encyclopedia: dict
) -> None:
    """draw all screen objects on screen."""
    # Draw a grey rectangle over all screen to blank
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
    window.blit(screen, (0, 0))

    # Draw a black rectange for sprite options to sit on
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

    # Draw a white rectange for the currently selected sprite
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

    drawselectables(encyclopedia, window)


def flip_display(encyclopedia: dict, window: pg.surface.Surface) -> pg.surface.Surface:
    """take background data and drawer it to the display"""
    backgroundmap = [
        [cellinterp(encyclopedia, cell, "Surface") for cell in row1]
        for row1 in Background_Data
    ]
    screensurf = createmapsurf(backgroundmap, CamPos[1], CamPos[0], Zoom)
    drawscreen(screensurf, window, encyclopedia)
    pg.display.flip()
    return screensurf


def drawselectables(encyclopedia: dict, window: pg.surface.Surface) -> None:
    """Place selectable options for each entry in the encyclopedia."""
    for surfnum, surf in enumerate(encyclopedia):
        window.blit(
            encyclopedia[surf]["Surface"],
            (
                (surfnum * 1.09) * Config["SpriteRes"] + Config["SpriteRes"],
                NewRes * Config["Height"] + Config["SpriteRes"],
            ),
            (0, 0, Config["SpriteRes"], Config["SpriteRes"]),
        )


def createmapsurf(maplist: list, top: int, left: int, zoom: int) -> pg.Surface:
    """loop over every tile on display and create a surface of the map."""
    mapsurf = pg.Surface((Config["Width"] * NewRes, Config["Height"] * NewRes + NewRes))
    for i2 in range(ceil(Config["Width"] * (Config["WindowScale"] / zoom))):
        if -1 < i2 + left < len(maplist[1]):  # only run if in range
            for j in range(
                (1 + Config["WindowScale"] - Zoom)
                + ceil(Config["Height"] * (Config["WindowScale"] / zoom))
            ):
                if -1 < j + top < len(maplist):  # only run if in range
                    tile1 = maplist[(j + top) % len(maplist)][
                        (i2 + left) % len(maplist[1])
                    ]
                    for surf in tile1:
                        w, h = surf.get_size()
                        mapsurf.blit(
                            pg.transform.scale(surf, (zoom * w, zoom * h)),
                            (
                                i2 * Config["SpriteRes"] * zoom,
                                j * Config["SpriteRes"] * zoom,
                            ),
                            (
                                0,
                                0,
                                Config["SpriteRes"] * zoom,
                                Config["SpriteRes"] * zoom,
                            ),
                        )
    return mapsurf


def selecttile(click: tuple[int, int], dictionary) -> str:
    """retuns the key of the clicked selectable."""
    index = floor(click[0] / (Config["SpriteRes"] + 2) - 1)
    return list(dictionary)[index]


def clickedindex(click: tuple, campos: list, meta_data: dict) -> tuple:
    """return the row and column of the clicked tile."""
    index = [
        (floor(coord / (Config["SpriteRes"] * Zoom)) + campos[i])
        % meta_data["MapSize"][i]
        for i, coord in enumerate(click)
    ]

    return tuple(index)


def writemappickle(dat: list) -> None:
    """Save the map file to a pickle."""
    with open("../maps/map1.map", "wb") as file:
        pickle.dump(dat, file)


def applytile(maplist: list, tile: str, tiletype: int) -> list:
    """Take the current selected tile object and paint to map."""
    match tiletype:
        case "Tile":
            liststr = list(maplist)
            liststr[0] = tile
            maplist = liststr
        case "Ent":
            tile = tile
            maplist.append(tile)
        case _:
            warn("Tile type not expected")

    return maplist


def drawbox(window: pg.surface.Surface, encyclopedia: dict) -> None:
    """drawer the selection box when draggiong."""
    global ScreenSurf
    global ClickDown

    mousepos = pg.mouse.get_pos()
    drawscreen(ScreenSurf, window, encyclopedia)
    pg.draw.rect(
        window,
        (255, 255, 255),
        pg.Rect(
            min(ClickDown[0], mousepos[0]),
            min(ClickDown[1], mousepos[1]),
            abs(mousepos[0] - ClickDown[0]),
            abs(mousepos[1] - ClickDown[1]),
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


# TODO Break up function
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

            # use arrow keys to navigate the map
            case pg.KEYDOWN:
                Redraw = True
                if event.key == pg.K_UP:
                    CamPos[1] = CamPos[1] - 1
                if event.key == pg.K_DOWN:
                    CamPos[1] = CamPos[1] + 1
                if event.key == pg.K_LEFT:
                    CamPos[0] = CamPos[0] - 1
                if event.key == pg.K_RIGHT:
                    CamPos[0] = CamPos[0] + 1

            case pg.MOUSEBUTTONDOWN:
                MouseDown = True
                # on left click
                if event.button == pg.BUTTON_LEFT:
                    Redraw = True
                    ClickDown = pg.mouse.get_pos()

                    # If clicking on editable area apply currently selected entity
                    if (
                        ClickDown[1] < Config["Height"] * NewRes
                        and encyclopedia[SelectedTile]["Type"] == "Ent"
                    ):
                        ActionFlag = False  # reset the save timer
                        pg.display.set_caption(f"Frog game editor{FileName} (Unsaved)")
                        ind = clickedindex(ClickDown, CamPos, meta)
                        Background_Data[ind[1]][ind[0]] = applytile(
                            Background_Data[ind[1]][ind[0]],
                            SelectedTile,
                            encyclopedia[SelectedTile]["Type"],
                        )

                    # If clicking on tile selection area change paintbrush tile
                    if (
                        Config["Height"] * NewRes + Config["SpriteRes"]
                        < ClickDown[1]
                        < Config["Height"] * NewRes + (2 * Config["SpriteRes"])
                    ):
                        SelectedTile = selecttile(ClickDown, encyclopedia)

                # on right click delet top entity
                if event.button == pg.BUTTON_RIGHT:
                    ClickDown = pg.mouse.get_pos()

                    # Remove top entity if it exists
                    if ClickDown[1] < Config["Height"] * NewRes:
                        ind = clickedindex(ClickDown, CamPos, meta)
                        if len(Background_Data[ind[1]][ind[0]]) > 1:
                            ActionFlag = False  # reset the save timer
                            Redraw = True
                            pg.display.set_caption(
                                f"Frog game editor{FileName} (Unsaved)"
                            )
                            Background_Data[ind[1]][ind[0]] = Background_Data[ind[1]][
                                ind[0]
                            ][:-1]

            # if clickup with background tile type selected do a drag
            case pg.MOUSEBUTTONUP:
                MouseDown = False
                if (
                    encyclopedia[SelectedTile]["Type"] == "Tile"
                    and event.button == pg.BUTTON_LEFT
                ):
                    click_up = pg.mouse.get_pos()
                    if click_up[1] < Config["Height"] * NewRes > ClickDown[1]:
                        Redraw = True
                        ActionFlag = False  # reset the save timer
                        pg.display.set_caption(f"Frog game editor{FileName} (Unsaved)")

                        index_down = clickedindex(ClickDown, CamPos, meta)
                        index_up = clickedindex(click_up, CamPos, meta)

                        rows = index_up[1] - index_down[1]
                        cols = index_up[0] - index_down[0]

                        rs = -1 if rows < 0 else 1
                        rows = abs(rows) + 1

                        cs = -1 if cols < 0 else 1
                        cols = abs(cols) + 1

                        for r, c in itertools.product(range(rows), range(cols)):
                            themap = applytile(
                                Background_Data[index_down[1] + (r * rs)][
                                    index_down[0] + (c * cs)
                                ],
                                SelectedTile,
                                encyclopedia[SelectedTile]["Type"],
                            )
                            Background_Data[index_down[1] + (r * rs)][
                                index_down[0] + (c * cs)
                            ] = themap

            # on scroll zoom
            case pg.MOUSEWHEEL:
                if int(round(time() * 1000)) > debounce:
                    Redraw = True
                    debounce = int(round(time() * Config["Debounce"])) + 150
                    Zoom = Zoom + event.y
                    Zoom = max(Zoom, 1)
                    Zoom = (
                        Config["WindowScale"] if Zoom > Config["WindowScale"] else Zoom
                    )

        # redarw map now button has been released
        if Redraw is True:
            ScreenSurf = flip_display(encyclopedia, window)
            Redraw = False

    # if mouse state is down draw box of selection
    if MouseDown and encyclopedia[SelectedTile]["Type"] == "Tile":
        drawbox(window, encyclopedia)

    # Save map to pickle file
    if ActionFlag is False:  # If an action occurs
        SaveCounter = 0  # Reset save delay
        ActionFlag = True  # Reset action flag to true

    SaveCounter += 1  # Increment counter eah time the code runs

    # Once save delay is met save the file
    if SaveCounter == SaveCycles:
        writemappickle([Background_Data, Foreground_Data])
        pg.display.set_caption(f"Frog game editor{FileName} (Saved)")


def load_save(meta_data) -> tuple[list, list]:
    """load map pickle and resize to match config file"""
    try:
        with open(f"../maps/{FileName}.map", "rb") as MapFile:
            data: List[list] = pickle.load(MapFile)
            background = data[0]
            foreground = data[1]
    except (FileNotFoundError, NameError):
        background = []
        foreground = []

    # import map dimentions from metadata file
    mapdims: List[int] = meta_data["MapSize"]

    background = resize_map_data(background, mapdims, "Stone")
    foreground = resize_map_data(foreground, mapdims, "InvisWall")

    return background, foreground


def main() -> None:
    global Background_Data, Foreground_Data
    with open(f"../maps/{FileName}.json") as mfile:
        metadata = load(mfile)

    Background_Data, Foreground_Data = load_save(metadata)

    window = pg.display.set_mode(
        (Config["Width"] * NewRes, Config["Height"] * NewRes + NewRes)
    )  # set display size

    # load in dicts
    encyclopedia = load_dicts(
        metadata, "Tiles", "Entities"
    )  # TODO use a class for tiles and ents

    pg.display.set_caption(f"Frog game editor{FileName}")

    flip_display(encyclopedia, window)

    # loop that runs eventhandler at specific rate
    while True:
        t1_start = perf_counter()

        event_handler(window, encyclopedia, metadata)

        fps_limiter(t1_start)


main()

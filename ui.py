from __future__ import annotations
from math import floor
from sys import stdout
from typing import TYPE_CHECKING
from colorama import Style, Back, Fore

if TYPE_CHECKING:
    from board import Board


_HIDE_CURSOR = "\033[?25l"
_BORDER_CHARS = {
    "single": {
        "topLeft": "┏",
        "topRight": "┓",
        "botLeft": "┗",
        "botRight": "┛",
        "horizontal": "━",
        "vertical": "┃",
    },
    "double": {
        "topLeft": "╔",
        "topRight": "╗",
        "botLeft": "╚",
        "botRight": "╝",
        "horizontal": "═",
        "vertical": "║",
    },
}
_TILE_CHARS = {"upper": {0: "┌─┐", 1: "▗▄▖"}, "lower": {0: "└─┘", 1: "▝▀▘"}}
_EXIT_CONTROLS = "\n* ESC para regresar/salir"


def _write(lines: str | list | tuple, newline: bool = True):
    if isinstance(lines, str):
        lines = [lines]
    stdout.write("\n".join(lines))
    if newline:
        stdout.write("\n")


def _drawTitle(title: str) -> int:
    padding = 44 if len(title) % 2 == 0 else 45
    frame = [
        "▁" * padding,
        f" {title.upper()} ".center(padding, "═"),
        "▔" * padding,
    ]
    _write(frame)
    return padding



def overwriteConsole():
    _write("\033[H\033[2J\033[3J", False)
    stdout.flush()


def hideCursor():
    _write(_HIDE_CURSOR)


def drawMenu(title: str, options: list | tuple, selectedIdx: int) -> int:
    overwriteConsole()
    width = _drawTitle(title)

    frame = []
    for i, option in enumerate(options):
        frame.append(
            f" > [ {Fore.LIGHTBLUE_EX + option + Style.RESET_ALL} ] < "
            if i == selectedIdx
            else f"     {option}"
        )

    _write(frame)
    _write(_EXIT_CONTROLS)
    return width


def drawAbout() -> int:
    overwriteConsole()
    width = _drawTitle("información")

    frame = [
        "Pixel Perfect - Inspirado por Mario Party 6",
        "",
        "Cómo jugar:",
        " - Copia el patrón mostrado al tablero",
        " - Utiliza W/A/S/D o ↑/←/↓/→ para navegar el tablero",
        " - Presiona ENTER o ESPACIO para cambiar el color de la celda",
        "",
        "Desarrolladores:",
        " - Baena Zamorano Leyla Elizabeth",
        " - Herrera Armenta Emmanuel",
        " - Sotelo Núñez Edgardo",
    ]

    _write(frame)
    _write(_EXIT_CONTROLS)
    return width


def drawSettings(options: list | tuple, selectedIdx: int) -> int:
    overwriteConsole()
    width = _drawTitle("configuración")

    frame = []
    for i, option in enumerate(options):
        match option["type"]:
            case "action":
                valueDisplay = ""
                frame.append("")
            case "int":
                valueDisplay = str(option["value"])
            case "bool":
                valueDisplay = "ON" if option["value"] else "OFF"
            case "time":
                valueDisplay = "OFF" if option["value"] == 0 else f"{option['value']}s"
        optionText = f"{option["label"].ljust(30)} {valueDisplay}"
        frame.append(
            f" > [ {Fore.LIGHTBLUE_EX + optionText + Style.RESET_ALL} ] < "
            if i == selectedIdx
            else f"     {optionText}"
        )

    _write(frame)
    _write(_EXIT_CONTROLS + ", A/S o ←/→ para configurar opción")
    return width


def drawBoard(board: Board):
    border = _BORDER_CHARS["double" if board.isInteractable else "single"]
    getUpper = lambda tile: _TILE_CHARS["upper"][tile]
    getLower = lambda tile: _TILE_CHARS["lower"][tile]
    getters = [getUpper, getLower]

    frame = [
        border["topLeft"]
        + border["horizontal"] * (board.size * 4 + 1)
        + border["topRight"]
    ]

    for i, row in enumerate(board.tiles):
        lines = []
        for k in range(len(getters)):
            lines.append(
                [
                    (
                        (Back.BLUE if [i, j] == board.selectedPos else "")
                        + getters[k](tile.value)
                        + Style.RESET_ALL
                        if board.isInteractable
                        else getters[k](tile.value)
                    )
                    for j, tile in enumerate(row)
                ]
            )
        frame += [
            f"{border['vertical']} {' '.join(line)} {border['vertical']}"
            for line in lines
        ]

    frame.append(
        border["botLeft"]
        + border["horizontal"] * (board.size * 4 + 1)
        + border["botRight"]
    )

    _write(frame)

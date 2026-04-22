from __future__ import annotations
from typing import TYPE_CHECKING
from sys import stdout
from colorama import Style, Back, Fore

if TYPE_CHECKING:
    from board import Board


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

def overwriteConsole(message="\033[H\033[2J\033[3J"):
    stdout.write(message)
    stdout.flush()


    border = _BORDER_CHARS["double" if board.allowInteract else "single"]
    frame = [
        border["topLeft"]
        + border["horizontal"] * (board.size * 4 + 1)
        + border["topRight"]
    ]
    getUpper = lambda tile: _TILE_CHARS["upper"][tile]
    getLower = lambda tile: _TILE_CHARS["lower"][tile]
    getters = [getUpper, getLower]
    for i, row in enumerate(board.tiles):
        lines = []
        for k in range(len(getters)):
            lines.append(
                [
                    (
                        (Back.BLUE if [i, j] == board.selectedPos else "")
                        + getters[k](tile.value)
                        + Style.RESET_ALL
                        if board.allowInteract
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
    stdout.write("\n".join(frame))

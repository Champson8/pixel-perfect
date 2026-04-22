from __future__ import annotations
from typing import TYPE_CHECKING
from sys import stdout
from colorama import Style, Back
from constants import BORDER_CHARS, TILE_CHARS


if TYPE_CHECKING:
    from board import Board


def overwriteConsole(message="\033[H\033[2J\033[3J"):
    stdout.write(message)
    stdout.flush()


def drawBoard(board: Board) -> str:
    border = BORDER_CHARS["double" if board.allowInteract else "single"]
    frame = [
        border["topLeft"]
        + border["horizontal"] * (board.size * 4 + 1)
        + border["topRight"]
    ]
    getUpper = lambda tile: TILE_CHARS["upper"][tile]
    getLower = lambda tile: TILE_CHARS["lower"][tile]
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

from __future__ import annotations
from math import ceil
from sys import stdout
from typing import TYPE_CHECKING
from colorama import Back, Fore

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


def _write(lines: str | list[str] | tuple[str], newline: bool = True):
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


def _getBoardDrawing(board: Board, centerToWidth: int = 0) -> str:
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
                        Back.BLUE + getters[k](tile.value) + Back.RESET
                        if board.isInteractable and [i, j] == board.selectedPos
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

    centeredFrame = []
    for line in frame:
        totalWidth = centerToWidth - 1
        if totalWidth % 2 == 0:
            totalWidth += 1
        if Back.BLUE in line:
            totalWidth += len(Back.BLUE)
        if Back.RESET in line:
            totalWidth += len(Back.RESET)
        centeredFrame.append(line.center(totalWidth))

    return "\n".join(centeredFrame) + "\n"


def _formattedSelectedOption(string: str):
    return f" > [ {Fore.LIGHTBLUE_EX + string + Fore.RESET} ] <"


def clearConsole():
    _write("\033[H\033[2J\033[3J", False)
    stdout.flush()


def hideCursor():
    _write(_HIDE_CURSOR)


def drawMenu(title: str, options: list[str] | tuple[str], selectedIdx: int) -> int:
    clearConsole()
    width = _drawTitle(title)

    frame = []
    for i, option in enumerate(options):
        frame.append(
            _formattedSelectedOption(option) if i == selectedIdx else f"     {option}"
        )

    _write(frame)
    _write(_EXIT_CONTROLS)
    return width


def drawAbout() -> int:
    clearConsole()
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


def drawSettings(options: list[dict] | tuple[dict], selectedIdx: int) -> int:
    clearConsole()
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
        descDisplay = (
            Fore.LIGHTBLACK_EX + f"  -  {option["description"]}" + Fore.RESET
            if option.get("description")
            else ""
        )
        scoreMultDisplay = (
            Fore.LIGHTBLACK_EX + f"Puntaje ×{option["scoreMultiplier"]}" + Fore.RESET
            if option.get("scoreMultiplier")
            else ""
        )
        optionText = f"{option["label"].ljust(30)} {valueDisplay}"
        frame.append(
            _formattedSelectedOption(optionText) + f"{descDisplay} {scoreMultDisplay}"
            if i == selectedIdx
            else f"     {optionText}"
        )

    _write(frame)
    _write(_EXIT_CONTROLS + ", A/S o ←/→ para configurar opción")
    return width


def drawRoundHUD(roundNumber: int, time: int | float = -1) -> int:
    clearConsole()
    width = _drawTitle(f"ronda #{roundNumber}")
    if time >= 0:
        _write(f"> {ceil(time)}s <".center(width) + "\n")
    return width


def drawStatsSummary(stats: dict[str, str | float], centerToWidth: int = 0):
    frame = []
    longestValLength = max(len(str(val)) for val in stats.values)
    for key, val in stats.items():
        keyDisplay = (key + ":").ljust(25)
        valDisplay = str(val).ljust(longestValLength)
        frame.append(f"{keyDisplay} {valDisplay}".center(centerToWidth))
    _write(frame)


def drawGameOver(title: str, stats: dict[str, str | float]):
    width = _drawTitle(title)
    drawStatsSummary(stats, width)
    _write("\n" + _formattedSelectedOption("Guardar Resultados"))
    _write(_EXIT_CONTROLS)


def drawBoards(*boards: Board, separator: str = "", centerToWidth: int = 0):
    frame = []
    for board in boards:
        frame.append(_getBoardDrawing(board, centerToWidth))
    _write(f"{separator.center(centerToWidth if separator else 0, "⋅")}\n".join(frame))

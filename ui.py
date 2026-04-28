from __future__ import annotations
from math import ceil
from sys import stdout
from typing import TYPE_CHECKING
from colorama import Back, Fore

if TYPE_CHECKING:
    from board import Board


_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"
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
_TILE_CHARS = {
    "upper": {-1: "╔╦╗", 0: "┌─┐", 1: "▗▄▖"},
    "lower": {-1: "╚╩╝", 0: "└─┘", 1: "▝▀▘"},
}
_EXIT_CONTROLS = Fore.LIGHTBLACK_EX + "\n* ESC para regresar/salir" + Fore.RESET
_COLORAMA_CODES = [*vars(Back).values(), *vars(Fore).values()]


def _write(lines: str | list[str] | tuple[str], newline: bool = True):
    if isinstance(lines, str):
        lines = [lines]
    stdout.write("\n".join(lines))
    if newline:
        stdout.write("\n")


def _drawTitle(title: str, baseWidth: int = 45) -> int:
    padding = baseWidth if len(title) % 2 == 1 else baseWidth - 1
    frame = [
        "▁" * padding,
        Fore.GREEN + f" {title.upper()} ".center(padding, "═") + Fore.RESET,
        "▔" * padding,
    ]
    _write(frame)
    return padding


def _formattedTile(
    board: Board, tileValue: int, tilePos: list | tuple, getter, overrides: dict
) -> str:
    tileStr = getter(tileValue)
    if tileValue == -1:
        tileStr = Fore.BLUE + tileStr + Fore.RESET
    if tuple(tilePos) in overrides:
        style = overrides[tuple(tilePos)]
        if style == "RED":
            tileStr = Back.RED + getter(tileValue) + Back.RESET
        elif style == "GRAY":
            tileStr = Back.LIGHTBLACK_EX + getter(tileValue) + Back.RESET
        elif style == "HIDDEN":
            tileStr = "   "
        elif style == "NONE":
            pass
    elif board.isInteractable and tuple(tilePos) == board.selectedPos:
        tileStr = Back.BLUE + getter(tileValue) + Back.RESET
    return tileStr


def _getUpperTileChars(tileValue: int) -> str:
    return _TILE_CHARS["upper"][tileValue]


def _getLowerTileChars(tileValue: int) -> str:
    return _TILE_CHARS["lower"][tileValue]


def _getBoardDrawing(board: Board, centerToWidth: int = 0, overrides: dict = {}) -> str:
    border = _BORDER_CHARS["double" if board.isInteractable else "single"]
    getters = [_getUpperTileChars, _getLowerTileChars]

    frame = [
        border["topLeft"]
        + border["horizontal"] * (board.size * 4 + 1)
        + border["topRight"]
    ]

    for i, row in enumerate(board.tiles):
        lines = []
        for getter in getters:

            lines.append(
                [
                    _formattedTile(board, tile.value, (i, j), getter, overrides)
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
        for code in _COLORAMA_CODES:
            if code in line:
                totalWidth += len(code) * line.count(code)
        centeredFrame.append(line.center(totalWidth))

    return "\n".join(centeredFrame) + "\n"


def _formattedSelectedOption(string: str):
    return f" > [ {Fore.LIGHTBLUE_EX + string + Fore.RESET} ] <"


def clearConsole():
    _write("\033[H\033[2J\033[3J", False)
    stdout.flush()


def hideCursor():
    _write(_HIDE_CURSOR)


def showCursor():
    _write(_SHOW_CURSOR)


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
        if option["type"] == "action":
            optionText = option["label"]
        else:
            optionText = f"{option["label"].ljust(30)} {valueDisplay}"
        frame.append(
            _formattedSelectedOption(optionText) + f"{descDisplay} {scoreMultDisplay}"
            if i == selectedIdx
            else f"     {optionText}"
        )
        if option.get("newlineAfter"):
            frame.append("")

    _write(frame)
    _write(
        _EXIT_CONTROLS
        + Fore.LIGHTBLACK_EX
        + ", A/S o ←/→ para configurar opción"
        + Fore.RESET
    )
    return width


def drawRoundHUD(roundNumber: int, time: int | float = -1) -> int:
    clearConsole()
    width = _drawTitle(f"ronda #{roundNumber}")
    if time >= 0:
        _write(f"> {ceil(time)}s <".center(width) + "\n")
    return width


def drawStatsSummary(stats: dict[str, str | float], centerToWidth: int = 0):
    frame = []
    longestValLength = max(len(str(val)) for val in stats.values())
    for key, val in stats.items():
        keyDisplay = (key + ":").ljust(25)
        valDisplay = str(val).ljust(longestValLength)
        frame.append(f"{keyDisplay} {valDisplay}".center(centerToWidth))
    _write(frame)


def drawGameOver(title: str, stats: dict[str, str | float], showOptions: bool = True):
    width = _drawTitle(title)
    drawStatsSummary(stats, width)
    if showOptions:
        _write("\n" + _formattedSelectedOption("Guardar Resultados"))
        _write(_EXIT_CONTROLS)


def drawBoards(
    *boards: Board,
    separator: str = "",
    centerToWidth: int = 0,
    overrides: dict[tuple | str, str] = {},
):
    """Draws the Board instances passed to it to the terminal.

    Args:
        separator (str, optional):
            Text to print in-between each board drawing.
            Defaults to "".
        centerToWidth (int, optional):
            Width to center the boards to.
            Defaults to 0.
        overrides (dict[tuple  |  str, str], optional):
            Overrides for tile-styling.
            May take a 'base overrides' dictionary to apply to all boards, or a dictionary where each key, value pair is a board id (str), 'base overrides' pair to apply to each board separately.
            A 'base overrides' dictionary (dict[tuple, str]) is one where each key, value pair is a tile position (tuple), style (str) pair.
            Defaults to {}.

    Raises:
        ValueError: If overrides' keys are not all of type 'tuple' or not all of type 'str'.
    """
    globalOverrides = True
    if overrides:
        if all(isinstance(key, str) for key in overrides.keys()):
            globalOverrides = False
        elif not any(isinstance(key, tuple) for key in overrides.keys()):
            raise ValueError(
                "'overrides' keys must all be of type 'tuple' or all of type 'str'."
            )
    getBoardOverrides = lambda board: (
        overrides if globalOverrides else overrides.get(board.id)
    )
    frame = []
    for board in boards:
        frame.append(
            _getBoardDrawing(board, centerToWidth, getBoardOverrides(board) or {})
        )
    _write(f"{separator.center(centerToWidth if separator else 0, "⋅")}\n".join(frame))


def drawLeaderboard(lbData: list[dict], highlightRowIdx: int = None):
    clearConsole()

    if lbData:
        headerRowCols = [" LUGAR"]
        for key in lbData[0].keys():
            headerRowCols.append(key.upper())
        headerRow = " | ".join(headerRowCols) + " "

        longestRowWidth = 0
        frame = [headerRow, "─"]
        for i, entry in enumerate(lbData):
            rank = str(i + 1).center(5)
            name = entry["Jugador"].center(7)
            score = entry["Puntaje"].rjust(7)
            rounds = entry["Rondas"].center(6)
            time = entry["Tiempo"].rjust(6)
            moves = entry["Movimientos"].center(11)
            accuracy = entry["Precision"].rjust(9)
            modes = entry["Modos"]

            rowText = f" {rank} | {name} | {score} | {rounds} | {time} | {moves} | {accuracy} | {modes} "
            if len(rowText) > longestRowWidth:
                longestRowWidth = len(rowText)
            if i == highlightRowIdx:
                rowText = Fore.YELLOW + rowText + Fore.RESET

            frame.append(rowText)

        frame[1] *= longestRowWidth
        _drawTitle("leaderboard", longestRowWidth)
        _write(frame)
    else:
        width = _drawTitle("leaderboard")
        _write("No hay resultados guardados.".center(width))

    _write(_EXIT_CONTROLS)

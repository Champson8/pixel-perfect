from copy import deepcopy
from dataclasses import dataclass
from random import random, randint, choice
from colorama import Back
from player import Player
from enums import InitialBoardState
from utils import defaultMutable, rotateMatrixLeft, rotateMatrixRight, resetStyleAfter
from constants import BORDER_CHARS, TILE_CHARS


@dataclass
class Board:
    size: int
    tiles: list[list[int]] = defaultMutable([[]])
    allowInteract: bool = False
    selectedPos: list[int] = defaultMutable([0, 0])

    def __post_init__(self):
        if self.size % 2 == 1:
            raise ValueError("Size must be an even number.")
        if self.allowInteract:
            self.player = Player(self)
        self.symmetryType = None  # 2 = two-way symmetry; 4 = four-way symmetry
        self.tiles: list[list[_Tile]] = self._intsToTiles(self.tiles)

    def __getitem__(self, key: list | tuple):
        if not isinstance(key, list | tuple):
            raise TypeError(
                "Index must be of type 'list' or 'tuple' with i, j coordinates."
            )
        return self.tiles[key[0]][key[1]]

    def __str__(self):
        border = BORDER_CHARS["double" if self.allowInteract else "single"]
        frame = [
            border["topLeft"]
            + border["horizontal"] * (self.size * 4 + 1)
            + border["topRight"]
        ]
        for i, row in enumerate(self.tiles):
            getUpper = lambda tile: TILE_CHARS["upper"][tile]
            getLower = lambda tile: TILE_CHARS["lower"][tile]
            getters = [getUpper, getLower]
            lines = []
            for k in range(len(getters)):
                lines.append(
                    [
                        (
                            self._styleIfSelected(getters[k](tile.value), i, j)
                            if self.allowInteract
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
            + border["horizontal"] * (self.size * 4 + 1)
            + border["botRight"]
        )
        return "\n".join(frame)

    def _intsToTiles(self, tiles: list[list[int | _Tile]]) -> list[list[_Tile]]:
        return [[_Tile(x) if isinstance(x, int) else x for x in row] for row in tiles]

    def _getSymmetricCoords(self, i: int, j: int) -> list[tuple]:
        coords = [(i, j)]
        if self.symmetryType == 2:
            coords += [(-(i + 1), -(j + 1))]
        else:
            currI, currJ = i, j
            for _ in range(3):
                newI, newJ = -(currJ + 1), currI
                coords.append((newI, newJ))
                currI, currJ = newI, newJ
        return coords

    def _styleIfSelected(self, string: str, posI: int, posJ: int) -> str:
        if [posI, posJ] == self.selectedPos:
            string = Back.BLUE + string
        return resetStyleAfter(string)

    def generateBase(self, initialState: InitialBoardState = InitialBoardState.PATTERN):
        if initialState not in InitialBoardState:
            initialState = InitialBoardState.PATTERN

        self.symmetryType = choice([2, 4])
        match initialState:
            case InitialBoardState.BLANK:
                newTiles = [[0] * self.size for _ in range(self.size)]
            case InitialBoardState.RANDOM:
                newTiles = [
                    [randint(0, 1) for _ in range(self.size)] for _ in range(self.size)
                ]
            case InitialBoardState.PATTERN:
                halfSize = self.size // 2
                newTiles = [[0] * self.size for _ in range(self.size)]

                for i in range(halfSize):
                    for j in range(halfSize):
                        if randint(0, 1):
                            for symI, symJ in self._getSymmetricCoords(i, j):
                                newTiles[symI][symJ] = 1

        self.tiles = self._intsToTiles(newTiles)


@dataclass
class _Tile:
    value: int

    def __post_init__(self):
        if self.value not in [0, 1]:
            raise ValueError("Value must be either a 0 or 1.")

    def flip(self):
        self.value = 1 - self.value

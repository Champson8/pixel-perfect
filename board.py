from dataclasses import dataclass
from random import randint
from colorama import Back
from player import Player
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
                            self.styleTile(getters[k](tile), i, j)
                            if self.allowInteract
                            else getters[k](tile)
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

    def randomize(self):
        self.tiles = [
            [randint(0, 1) for _ in range(self.size)] for _ in range(self.size)
        ]

    def generatePattern(self):
        halfSize = self.size // 2
        basePattern = [
            [randint(0, 1) for _ in range(halfSize)] for _ in range(halfSize)
        ]

        newBoard = lowerHalf = list()
        twoWay = bool(randint(0, 1))
        fourWay = not twoWay
        rotate = rotateMatrixRight if randint(0, 1) == 1 else rotateMatrixLeft

        for i in range(self.size):
            if i < halfSize:
                newBoard += [
                    basePattern[i]
                    + (rotate(basePattern)[i] if fourWay else basePattern[i])
                ]
            else:
                newBoard += [[0] * self.size]

        lowerHalf = rotate(newBoard, 2)
        for i in range(halfSize, self.size):
            newBoard[i] = lowerHalf[i]

        self.tiles = newBoard

    def styleTile(self, string, posI, posJ):
        if [posI, posJ] == self.selectedPos:
            string = Back.BLUE + string
        return resetStyleAfter(string)

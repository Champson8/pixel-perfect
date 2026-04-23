from copy import deepcopy
from dataclasses import dataclass
from random import random, randint, choice
from enums import InitialBoardState
from utils import defaultMutable


@dataclass
class Board:
    size: int
    tiles: list[list[int]] = defaultMutable([[]])
    isInteractable: bool = False

    def __post_init__(self):
        if self.size % 2 == 1:
            raise ValueError("Size must be an even number.")
        self.selectedPos = [0, 0]
        self.symmetryType = None  # 2 = two-way symmetry; 4 = four-way symmetry
        self.tiles: list[list[_Tile]] = self._intsToTiles(self.tiles)

    def __getitem__(self, key: list | tuple) -> _Tile:
        if not isinstance(key, list | tuple):
            raise TypeError(
                "Index must be of type 'list' or 'tuple' with i, j coordinates."
            )
        return self.tiles[key[0]][key[1]]

    def __eq__(self, other: Board):
        if not isinstance(other, Board):
            raise TypeError("Both items in comparison must be of type 'Board'.")
        return self._tilesToInts(self.tiles) == other._tilesToInts(other.tiles)

    def _intsToTiles(self, tiles: list[list[int | _Tile]]) -> list[list[_Tile]]:
        return [[_Tile(x) if isinstance(x, int) else x for x in row] for row in tiles]

    def _tilesToInts(self, tiles: list[list[int | _Tile]]) -> list[list[int]]:
        return [
            [tile.value if isinstance(tile, _Tile) else tile for tile in row]
            for row in tiles
        ]

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

    def flipSelectedTile(self):
        self[self.selectedPos].flip()

    def moveSelection(self, newI: int, newJ: int):
        self.selectedPos = [newI, newJ]

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

    def mutated(
        self,
        willBeInteractable: bool = False,
        mutationCount: int = 0,
        spreadFactor: float = 0.0,
        symmetryWeight: float = 1.0,
    ) -> Board:
        """Creates and returns a new Board instance based on the original instance's tileset.

        Args:
            mutationCount (int, optional):
                Number of tiles to flip.
                Defaults to 0.
            spreadFactor (float, optional):
                Chance to flip random tiles opposed to adjacent ones.
                Defaults to 0.0.
            symmetryWeight (float, optional):
                Chance to respect board's symmetry type.
                Defaults to 1.0.

        Raises:
            ValueError: If mutationCount or spreadFactor or symmetryWeight < 0.
            ValueError: If mutationCount > number of tiles.
            ValueError: If spreadFactor or symmetryWeight > 1.

        Returns:
            Board: Instance with mutated tiles.
        """
        if mutationCount < 0 or spreadFactor < 0 or symmetryWeight < 0:
            raise ValueError(
                "Mutation count, spread factor and symmetry weight cannot be less than 0."
            )
        if mutationCount > self.size**2:
            raise ValueError("Mutation count cannot be higher than number of tiles.")
        if spreadFactor > 1 or symmetryWeight > 1:
            raise ValueError(
                "Spread factor and symmetry weight cannot be higher than 1."
            )

        newBoard = Board(
            self.size, deepcopy(self.tiles), isInteractable=willBeInteractable
        )

        randomCoords = lambda: (randint(0, self.size - 1), randint(0, self.size - 1))
        firstMutationDone = False
        lastCoords = None
        while mutationCount > 0:
            startCoords = randomCoords()
            if firstMutationDone:
                if random() > spreadFactor:
                    axisIndex = randint(0, 1)
                    increment = choice([1, -1])
                    if (lastCoords[axisIndex] == 0 and increment == -1) or (
                        lastCoords[axisIndex] == self.size - 1 and increment == 1
                    ):
                        increment = 0 - increment
                    if axisIndex:
                        startCoords = (lastCoords[0], lastCoords[1] + increment)
                    else:
                        startCoords = (lastCoords[0] + increment, lastCoords[1])
            else:
                firstMutationDone = True
            if random() < symmetryWeight:
                tilesToFlip = self._getSymmetricCoords(startCoords[0], startCoords[1])
            else:
                tilesToFlip = [startCoords]
            for position in tilesToFlip:
                newBoard[position].flip()
            lastCoords = startCoords
            mutationCount -= 1

        return newBoard


@dataclass
class _Tile:
    value: int

    def __post_init__(self):
        if self.value not in [0, 1]:
            raise ValueError("Value must be either a 0 or 1.")

    def flip(self):
        self.value = 1 - self.value

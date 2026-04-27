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
    id: str = None

    def __post_init__(self):
        if self.size % 2 == 1:
            raise ValueError("Size must be an even number.")
        self.selectedPos = (0, 0)
        self.symmetryType = None  # 2 = two-way symmetry; 4 = four-way symmetry
        self.tiles: list[list[_Tile]] = self._intsToTiles(self.tiles)
        if self.tiles[0]:
            self._moveSelectedPosUntilValid()

    def __getitem__(self, key: list | tuple) -> _Tile:
        if not isinstance(key, list | tuple):
            raise TypeError(
                "Index must be of type 'list' or 'tuple' with i, j coordinates."
            )
        return self.tiles[key[0]][key[1]]

    def __eq__(self, other: Board) -> bool:
        if not isinstance(other, Board):
            raise TypeError("Both items in comparison must be of type 'Board'.")
        return self._tilesToInts(self.tiles) == other._tilesToInts(other.tiles)

    @property
    def _numAvailableTiles(self) -> int:
        return self.size**2 - sum(
            row.count(-1) for row in self._tilesToInts(self.tiles)
        )

    @property
    def _areAllTilesAccessible(self) -> bool:
        accessibleTiles = []
        randomPos = self.getRandomPos()

        def checkAdjacentTiles(tilePos: tuple):
            try:
                if (
                    tilePos[0] < 0
                    or tilePos[1] < 0
                    or self[tilePos].value == -1
                    or tilePos in accessibleTiles
                ):
                    raise Exception
            except:
                return
            accessibleTiles.append(tilePos)
            for posMoves in [[-1, 0], [0, 1], [1, 0], [0, -1]]:
                newPos = (tilePos[0] + posMoves[0], tilePos[1] + posMoves[1])
                checkAdjacentTiles(newPos)

        checkAdjacentTiles(randomPos)

        return len(accessibleTiles) == self._numAvailableTiles

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

    def _moveSelectedPosUntilValid(self):
        while self[self.selectedPos].value == -1:
            self.selectedPos = tuple(map(lambda n: n + 1, self.selectedPos))

    def flipSelectedTile(self):
        self[self.selectedPos].flip()

    def flipTile(self, position: tuple):
        self[position].flip()

    def moveSelection(self, newI: int, newJ: int):
        if self[newI, newJ].value != -1:
            self.selectedPos = (newI, newJ)

    def getRandomPos(self) -> tuple:
        randomPos = None
        while randomPos is None or self[randomPos].value == -1:
            randomPos = (randint(0, self.size - 1), randint(0, self.size - 1))
        return randomPos

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

    def toMutated(
        self,
        willBeInteractable: bool = False,
        mutationCount: int = 0,
        spreadFactor: float = 0.0,
        symmetryWeight: float = 1.0,
        newId: str = None,
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
            self.size, deepcopy(self.tiles), isInteractable=willBeInteractable, id=newId
        )

        originalMutations = mutationCount
        while newBoard == self:
            randomCoords = lambda: (
                randint(0, self.size - 1),
                randint(0, self.size - 1),
            )
            firstMutationDone = False
            lastCoords = None
            mutationCount = originalMutations
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
                    tilesToFlip = self._getSymmetricCoords(
                        startCoords[0], startCoords[1]
                    )
                else:
                    tilesToFlip = [startCoords]
                for position in tilesToFlip:
                    if newBoard[position].value != -1:
                        newBoard.flipTile(position)
                lastCoords = startCoords
                mutationCount -= 1

        return newBoard

    def addObstacles(self):
        originalTiles = deepcopy(self.tiles)
        numObstPerQuadr = None

        match self.size:
            case 4:
                numObstPerQuadr = 1
            case 6:
                numObstPerQuadr = randint(2, 3)
            case 8:
                numObstPerQuadr = randint(3, 5)
            case 10:
                numObstPerQuadr = randint(4, 6)

        while True:
            newTiles = deepcopy(originalTiles)
            obstPosQuadr = []
            while len(obstPosQuadr) < numObstPerQuadr:
                randomQuadrPos = tuple(map(lambda n: n // 2, self.getRandomPos()))
                if randomQuadrPos not in obstPosQuadr:
                    obstPosQuadr.append(randomQuadrPos)

            for position in obstPosQuadr:
                for symI, symJ in self._getSymmetricCoords(position[0], position[1]):
                    newTiles[symI][symJ] = _Tile(-1)

            self.tiles = newTiles
            if self._areAllTilesAccessible:
                break


@dataclass
class _Tile:
    value: int

    def __post_init__(self):
        if self.value not in [-1, 0, 1]:
            raise ValueError("Value must be either -1, 0 or 1.")

    def flip(self):
        self.value = 1 - self.value

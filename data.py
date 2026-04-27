from dataclasses import dataclass, field, fields


@dataclass
class GameSettings:
    """Stores a single game's settings.

    Attributes:
        boardSize (int, optional):
            Size of the square board.
            Defaults to 4.
        totalRounds (int, optional):
            Number of rounds in the game.
            Defaults to 10.
        timeLimit (int, optional):
            Time limit in seconds before automatic failure each round, 0 means no time limit.
            Defaults to 0.
        hideTargetAfter (int, optional):
            Time in seconds after which the target board will be hidden, 0 means no hiding, timeLimit must not be 0.
            Defaults to 0.
        suddenDeath (bool, optional):
            Whether to automatically fail a round if a single tile flip is erroneous.
            Defaults to False.
        obstacles (bool, optional):
            Whether to generate both boards with non-interactable tiles in them.
            Defaults to False.
        chaosFlipping (bool, optional):
            Whether to periodically automatically flip random tiles on the player board.
            Defaults to False.
    """

    boardSize: int = field(
        default=4,
        metadata={
            "label": "Tamaño del Tablero",
            "type": "int",
            "min": 4,
            "max": 10,
            "step": 2,
        },
    )
    totalRounds: int = field(
        default=5,
        metadata={
            "label": "Número de Rondas",
            "type": "int",
            "min": 3,
            "max": 10,
            "step": 1,
            "newlineAfter": True,
        },
    )
    timeLimit: int = field(
        default=0,
        metadata={
            "label": "Tiempo Límite",
            "type": "time",
            "min": 0,
            "max": 30,
            "step": 10,
            "newlineAfter": True,
        },
    )
    obstacles: bool = field(
        default=False,
        metadata={
            "label": "Obstáculos",
            "description": "Añade obstáculos en forma de celdas al tablero.",
            "type": "bool",
            "scoreMultiplier": 1.1,
        },
    )
    hideTargetAfter: int = field(
        default=0,
        metadata={
            "label": "Ocultar Patrón",
            "description": "Oculta el patrón a copiar después del tiempo especificado.",
            "type": "time",
            "min": 0,
            "max": 10,
            "step": 1,
            "scoreMultiplier": 1.2,
        },
    )
    inverseControls: bool = field(
        default=False,
        metadata={
            "label": "Invertir Controles",
            "description": "Invierte los controles de movimiento.",
            "type": "bool",
            "scoreMultiplier": 1.3,
        },
    )
    chaosFlipping: bool = field(
        default=False,
        metadata={
            "label": "Celdas Caóticas",
            "description": "Cambia celdas aleatorias periódicamente.",
            "type": "bool",
            "scoreMultiplier": 1.4,
        },
    )
    suddenDeath: bool = field(
        default=False,
        metadata={
            "label": "Muerte Súbita",
            "description": "Finaliza la ronda si cometes un error.",
            "type": "bool",
            "scoreMultiplier": 1.5,
            "newlineAfter": True,
        },
    )

    def _generateOptionsList(self) -> list[dict]:
        options = []
        for f in fields(self):
            item = {"id": f.name, "value": getattr(self, f.name), **f.metadata}
            options.append(item)
        options.append({"id": "start", "label": "Iniciar Juego", "type": "action"})
        return options


@dataclass
class StatsTracker:
    totalWonRounds: int = 0
    timeElapsed: float = 0
    totalMoves: int = 0
    totalFlips: int = 0
    totalMistakes: int = 0

    def __post_init__(self):
        self.accuracy: float = 0
        self.movesPerSecond: float = None
        self.score: int = None

    def calculateAccuracy(self):
        if self.totalFlips:
            self.accuracy = (
                (self.totalFlips - self.totalMistakes) / self.totalFlips * 100
            )

    def calculateMPS(self):
        self.movesPerSecond = self.totalMoves / self.timeElapsed

    def calculateScore(self, gameSettings: GameSettings):
        multiplier = 1
        for f in fields(gameSettings):
            md = f.metadata
            if md.get("scoreMultiplier") and bool(getattr(gameSettings, f.name)):
                multiplier += md["scoreMultiplier"] - 1
        boardSizeBonus = 100 * (gameSettings.boardSize - 4) / 2
        self.score = (
            (self.totalWonRounds * (1000 + boardSizeBonus))
            - (self.totalMistakes * 50)
            - (self.timeElapsed * 10)
            - self.totalMoves
        )
        self.score *= multiplier
        self.score = max(0, round(self.score))

    def getFormattedStats(self) -> dict:
        stats = {
            "Tiempo Total": f"{round(self.timeElapsed, 2)}s\n",
            "Total de Movimientos": self.totalMoves,
            "Movimientos por Segundo": f"{round(self.movesPerSecond, 2)}\n",
            "Total de Errores": self.totalMistakes,
            "Precisión": f"{round(self.accuracy, 2)}%\n",
            "Puntaje": self.score,
        }
        return stats

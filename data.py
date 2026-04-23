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
        autoRandomFlip (bool, optional):
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
        },
    )
    timeLimit: int = field(
        default=0,
        metadata={
            "label": "Tiempo Límite",
            "type": "time",
            "min": 0,
            "max": 60,
            "step": 10,
        },
    )
    hideTargetAfter: int = field(
        default=0,
        metadata={
            "label": "Tiempo para Memorizar Patrón",
            "type": "time",
            "min": 0,
            "max": 10,
            "step": 1,
        },
    )
    suddenDeath: bool = field(
        default=False, metadata={"label": "Muerte Súbita", "type": "bool"}
    )
    obstacles: bool = field(
        default=False, metadata={"label": "Obstáculos", "type": "bool"}
    )
    autoRandomFlip: bool = field(
        default=False, metadata={"label": "Cambiar Celdas Aleatorias", "type": "bool"}
    )

    def _generateOptionsList(self) -> list:
        options = []
        for f in fields(self):
            item = {"id": f.name, "value": getattr(self, f.name), **f.metadata}
            options.append(item)
        options.append({"id": "start", "label": "Iniciar Juego", "type": "action"})
        return options

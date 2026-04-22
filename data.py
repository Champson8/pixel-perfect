from dataclasses import dataclass


@dataclass
class GameSettings:
    boardSize: int = 4
    totalRounds: int = 10
    isTimed: bool = False
    timeLimit: int = 0  # 0 = no time limit
    suddenDeath: bool = False
    hideTargetAfter: int = 0  # 0 = target isn't hidden

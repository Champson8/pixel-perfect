from dataclasses import dataclass
from board import Board
from enums import GameState


@dataclass
class GameManager:
    state: GameState = GameState.TITLE
    settings: None
    stats: None

    def run(self):
        while True:
            match self.state:
                case GameState.TITLE:
                    pass
                case GameState.ABOUT:
                    pass
                case GameState.SETTINGS:
                    pass
                case GameState.PLAYING:
                    pass
                case GameState.OVER:
                    pass


@dataclass
class Round:
    targetBoard: Board
    playerBoard: Board
    mistakes: int = 0
    timeElapsed: int = 0

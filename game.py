from dataclasses import dataclass
import ui
from board import Board
from enums import GameState


class GameManager:
    def __init__(self):
        self.state: GameState = GameState.TITLE
        self.settings = None
        self.stats = None

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
                case GameState.LEADERBOARD:
                    pass
                case GameState.QUIT:
                    break


@dataclass
class Round:
    targetBoard: Board
    playerBoard: Board
    mistakes: int = 0
    timeElapsed: int = 0

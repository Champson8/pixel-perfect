from dataclasses import dataclass
import ui
from board import Board
from enums import GameState
from utils import getUserAction
from constants import HIDE_CURSOR


class GameManager:
    def __init__(self):
        self.state: GameState = GameState.TITLE
        self.settings = None
        self.stats = None

    def run(self):
        ui.overwriteConsole(HIDE_CURSOR)

        while True:
            match self.state:
                case GameState.TITLE:
                    self.handleTitleScreen()
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

    def handleTitleScreen(self):
        options = ["Jugar", "Leaderboard", "Información", "Salir"]
        numOptions = len(options)
        selected = 0

        while True:
            ui.drawMenu("Pixel Perfect", options, selected)

            action = getUserAction()

            match action:
                case "UP":
                    selected = (selected - 1) % numOptions
                case "DOWN":
                    selected = (selected + 1) % numOptions
                case "ENTER":
                    break

        match selected:
            case 0:
                pass
            case 1:
                pass
            case 2:
                self.state = GameState.ABOUT
            case 3:
                self.state = GameState.QUIT


@dataclass
class Round:
    targetBoard: Board
    playerBoard: Board
    mistakes: int = 0
    timeElapsed: int = 0

from dataclasses import dataclass
import ui
from board import Board
from data import GameSettings
from enums import GameState
from utils import getUserAction
from constants import HIDE_CURSOR


class GameManager:
    def __init__(self):
        self.state: GameState = GameState.TITLE
        self.settings = GameSettings()
        self.stats = None

    def run(self):
        ui.overwriteConsole(HIDE_CURSOR)

        while True:
            match self.state:
                case GameState.TITLE:
                    self.handleTitleScreen()
                case GameState.ABOUT:
                    self.handleAbout()
                case GameState.SETTINGS:
                    self.handleSettings()
                case GameState.PLAYING:
                    pass
                case GameState.OVER:
                    pass
                case GameState.LEADERBOARD:
                    pass
                case GameState.QUIT:
                    break

    def handleTitleScreen(self):
        options = ["Jugar", "Leaderboard", "Información"]
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
                case "ESCAPE":
                    self.state = GameState.QUIT
                    return

        states = [GameState.PLAYING, GameState.LEADERBOARD, GameState.ABOUT]
        self.state = states[selected]

    def handleAbout(self):
        ui.drawAbout()
        while True:
            action = getUserAction()
            if action == "ESCAPE":
                break
        self.state = GameState.TITLE

    def handleSettings(self):
        pass


@dataclass
class Round:
    targetBoard: Board
    playerBoard: Board
    mistakes: int = 0
    timeElapsed: int = 0

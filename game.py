from dataclasses import dataclass
from random import randint
import ui
from board import Board
from player import Player
from data import GameSettings
from enums import GameState, InitialBoardState
from utils import getLatestAction


class GameManager:
    def __init__(self):
        self.state: GameState = GameState.TITLE
        self.settings = GameSettings()
        self.stats = None

    def run(self):
        ui.hideCursor()

        while True:
            if self.state == GameState.QUIT:
                break
            else:
                {
                    GameState.TITLE: self.handleTitle,
                    GameState.ABOUT: self.handleAbout,
                    GameState.SETTINGS: self.handleSettings,
                    GameState.PLAYING: self.startGame,
                    GameState.OVER: lambda: None,
                    GameState.LEADERBOARD: lambda: None,
                }.get(self.state)()

    def handleTitle(self):
        options = ["Jugar", "Leaderboard", "Información"]
        numOptions = len(options)
        selected = 0

        while True:
            ui.drawMenu("Pixel Perfect", options, selected)

            action = getLatestAction()

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

        states = [GameState.SETTINGS, GameState.LEADERBOARD, GameState.ABOUT]
        self.state = states[selected]

    def handleAbout(self):
        ui.drawAbout()
        while True:
            action = getLatestAction()
            if action == "ESCAPE":
                break
        self.state = GameState.TITLE

    def handleSettings(self):
        options = self.settings._generateOptionsList()
        numOptions = len(options)
        selected = 0

        while True:
            ui.drawSettings(options, selected)

            currentOption = options[selected]
            action = getLatestAction()

            match action:
                case "UP":
                    selected = (selected - 1) % numOptions
                case "DOWN":
                    selected = (selected + 1) % numOptions
                case "LEFT" | "RIGHT":
                    if currentOption["type"] in ["int", "time"]:
                        step = currentOption["step"]
                        currentOption["value"] = (
                            max(currentOption["value"] - step, currentOption["min"])
                            if action == "LEFT"
                            else min(
                                currentOption["value"] + step, currentOption["max"]
                            )
                        )
                    elif currentOption["type"] == "bool":
                        currentOption["value"] = action == "RIGHT"
                    self.enforceSettingDependencies(options, currentOption)
                case "ENTER":
                    if currentOption["id"] == "start":
                        self.saveSettings(options)
                        self.state = GameState.PLAYING
                        return
                case "ESCAPE":
                    self.state = GameState.TITLE
                    return

    def enforceSettingDependencies(self, options: list | tuple, changedOption: dict):
        match changedOption["id"]:
            case "timeLimit":
                if changedOption["value"] == 0:
                    for option in options:
                        if option["id"] == "hideTargetAfter" and option["value"] > 0:
                            option["value"] = 0
            case "hideTargetAfter":
                if changedOption["value"] > 0:
                    for option in options:
                        if option["id"] == "timeLimit" and option["value"] == 0:
                            option["value"] = 30

    def saveSettings(self, options: list | tuple):
        for option in options:
            if option["type"] != "action":
                setattr(self.settings, option["id"], option["value"])

    def startGame(self):
        pass


@dataclass
class Round:
    roundNumber: int
    settings: GameSettings

    def __post_init__(self):
        self.targetBoard: Board = None
        self.playerBoard: Board = None
        self.player: Player = None
        self.boardConfig: dict = {}
        self.timeElapsed: int = 0
        self.mistakes: int = 0
        self.moves: int = 0

    def _setBoardConfig(self):
        difficulty = (self.roundNumber - 1) / (self.settings.totalRounds - 1)

        if difficulty <= 0.2:
            self.boardConfig = {
                "initialState": InitialBoardState.BLANK,
                "mutationsCount": randint(2, 5),
                "spreadFactor": 0.35,
                "symmetryWeight": 1,
            }
        elif difficulty <= 0.4:
            self.boardConfig = {
                "initialState": InitialBoardState.PATTERN,
                "mutationsCount": randint(3, 7),
                "spreadFactor": 0.2,
                "symmetryWeight": 0.85,
            }
        elif difficulty <= 0.7:
            self.boardConfig = {
                "initialState": InitialBoardState.PATTERN,
                "mutationsCount": randint(5, 9),
                "spreadFactor": 0.65,
                "symmetryWeight": 0.4,
            }
        elif difficulty <= 0.9:
            self.boardConfig = {
                "initialState": InitialBoardState.PATTERN,
                "mutationsCount": randint(8, 12),
                "spreadFactor": 0.8,
                "symmetryWeight": 0.1,
            }
        else:
            self.boardConfig = {
                "initialState": InitialBoardState.RANDOM,
                "mutationsCount": randint(10, 15),
                "spreadFactor": 0.9,
                "symmetryWeight": 0,
            }

    def _generateBoards(self):
        self._setBoardConfig()

        self.targetBoard = Board(self.settings.boardSize)
        self.targetBoard.generateBase(self.boardConfig["initialState"])

        self.playerBoard = self.targetBoard.mutated(
            True,
            self.boardConfig["mutationsCount"],
            self.boardConfig["spreadFactor"],
            self.boardConfig["symmetryWeight"],
        )

    def start(self):
        self._generateBoards()
        self.player = Player(self.playerBoard)

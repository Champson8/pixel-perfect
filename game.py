"""
Module to manage the game state.

This module handles the game menus, their display and navigation, as well as
the core functionality of each game loop and its rounds, all with the help of the other modules present.

Contributors:
    - Baena Zamorano Leyla Elizabeth (Sound effects)
    - Herrera Armenta Emmanuel (Menus, rounds, refactoring, testing)
    - Sotelo Núñez Edgardo (Settings menu, leaderboard)
"""

from dataclasses import dataclass
from json import load, dump, JSONDecodeError
from pathlib import Path
from queue import Empty
from random import randint
from time import perf_counter, sleep
import ui
from board import Board
from data import GameSettings, StatsTracker
from player import Player
from sound import SoundManager
from enums import GameState, InitialBoardState, SoundEffect
from utils import (
    getLatestAction,
    clearActionQueue,
    pauseActionListener,
    unpauseActionListener,
    setKbhitBypass,
)


class GameManager:
    def __init__(self):
        self.state: GameState = GameState.TITLE
        self.sounds = SoundManager()
        self.gameMusic = None

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
                    GameState.OVER: self.handleGameOver,
                    GameState.LEADERBOARD: self.handleLeaderboard,
                }.get(self.state)()

    def reset(self):
        self.settings = GameSettings()
        self.stats = StatsTracker()
        self.highlightLeaderboardIdx: int = None

    def handleTitle(self):
        self.reset()

        options = ["Jugar", "Leaderboard", "Información"]
        numOptions = len(options)
        selected = 0

        while True:
            ui.drawMenu("Pixel Perfect", options, selected)

            action = getLatestAction()

            match action:
                case "UP":
                    selected = (selected - 1) % numOptions
                    self.sounds.play(SoundEffect.MOVE)
                case "DOWN":
                    selected = (selected + 1) % numOptions
                    self.sounds.play(SoundEffect.MOVE)
                case "ENTER":
                    self.sounds.play(SoundEffect.INTERACT)
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
                    self.sounds.play(SoundEffect.MOVE)
                case "DOWN":
                    selected = (selected + 1) % numOptions
                    self.sounds.play(SoundEffect.MOVE)
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
                    if currentOption["id"] != "start":
                        self.sounds.play(SoundEffect.MOVE)
                case "ENTER":
                    if currentOption["id"] == "start":
                        self.saveSettings(options)
                        self.state = GameState.PLAYING
                        self.sounds.play(SoundEffect.INTERACT)
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
        self.gameMusic = self.sounds.play(SoundEffect.GAME, -1)
        for i in range(1, self.settings.totalRounds + 1):
            round = Round(i, self.settings, self.sounds)
            round.start()
            self.stats.totalWonRounds += int(round.won)
            self.stats.timeElapsed += round.timeElapsed
            self.stats.totalMoves += round.moves
            self.stats.totalFlips += round.flips
            self.stats.totalMistakes += round.mistakes
        self.state = GameState.OVER

    def handleGameOver(self):
        self.stats.calculateAccuracy()
        self.stats.calculateMPS()
        self.stats.calculateScore(self.settings)
        gameStatsSummary = self.stats.getFormattedStats()

        self.gameMusic.stop()
        self.sounds.play(SoundEffect.END)

        ui.clearConsole()
        ui.drawGameOver("resultados", gameStatsSummary)

        setKbhitBypass(False)
        action = getLatestAction()
        if action == "ENTER":
            pauseActionListener()

            ui.showCursor()
            self.sounds.play(SoundEffect.INTERACT)

            playerName = ""
            while not (
                len(playerName) == 3
                and playerName.isalnum()
                and not playerName.isdigit()
            ):
                ui.clearConsole()
                ui.drawGameOver("resultados", gameStatsSummary, False)
                playerName = input("\n Identificador (3 caracteres): ")
            playerName = playerName.upper()

            unpauseActionListener()
            ui.hideCursor()

            playerData = self.getFormattedPlayerData(playerName)
            playerRankIdx = self.saveResults(playerData)
            self.highlightLeaderboardIdx = playerRankIdx

            self.state = GameState.LEADERBOARD
        elif action == "ESCAPE":
            self.state = GameState.TITLE
        setKbhitBypass(True)

    def handleLeaderboard(self):
        lbData, _ = self.getLeaderboardData()

        ui.drawLeaderboard(lbData, self.highlightLeaderboardIdx)

        action = getLatestAction()
        if action == "ESCAPE":
            self.state = GameState.TITLE

    def getLeaderboardData(self) -> tuple[list[dict], Path]:
        lbPath = Path("leaderboard.json")

        if lbPath.exists():
            try:
                with open(lbPath.resolve()) as file:
                    lbData = load(file)
            except JSONDecodeError:
                lbData = []
        else:
            lbData = []

        return lbData, lbPath

    def saveResults(self, playerData: dict) -> int:
        lbData, lbPath = self.getLeaderboardData()

        lbData.append(playerData)
        lbData.sort(key=lambda x: int(x.get("Puntaje", 0)), reverse=True)
        lbData = lbData[:20]

        with open(lbPath.resolve(), "w") as f:
            dump(lbData, f, indent=4)

        return lbData.index(playerData)

    def getFormattedPlayerData(self, playerName: str) -> dict:
        MODE_CODES = {
            "obstacles": "OB",
            "hideTargetAfter": "OP",
            "inverseControls": "IC",
            "chaosFlipping": "CC",
            "suddenDeath": "MS",
        }
        data = {
            "Jugador": playerName,
            "Puntaje": str(self.stats.score),
            "Rondas": str(self.settings.totalRounds),
            "Tiempo": f"{round(self.stats.timeElapsed, 2)}s",
            "Movimientos": str(self.stats.totalMoves),
            "Precision": f"{round(self.stats.accuracy, 2)}%",
        }
        modes = []
        for mode, code in MODE_CODES.items():
            if getattr(self.settings, mode):
                modes.append(code)
        if modes:
            data["Modos"] = f"[{'] ['.join(modes)}]"
        else:
            data["Modos"] = "N/A"
        return data


@dataclass
class Round:
    roundNumber: int
    settings: GameSettings
    sounds: SoundManager

    def __post_init__(self):
        self.targetBoard: Board = None
        self.playerBoard: Board = None

        self.player: Player = None
        self.boardConfig: dict = {}

        self.timeElapsed: int = 0
        self.mistakes: int = 0
        self.moves: int = 0
        self.flips: int = 0

        self.didFatalMistake: bool = False
        self.hideTargetBoard: bool = False

        self.isOver: bool = False

    @property
    def won(self) -> bool:
        return self.playerBoard == self.targetBoard

    def _setBoardConfig(self):
        difficulty = (self.roundNumber - 1) / (self.settings.totalRounds - 1)
        mutationsMultiplier = (self.settings.boardSize - 4) // 2 + 1

        if difficulty <= 0.2:
            self.boardConfig = {
                "initialState": InitialBoardState.BLANK,
                "mutationsCount": randint(2, 5) * mutationsMultiplier,
                "spreadFactor": 0.35,
                "symmetryWeight": 1,
            }
        elif difficulty <= 0.4:
            self.boardConfig = {
                "initialState": InitialBoardState.PATTERN,
                "mutationsCount": randint(3, 7) * mutationsMultiplier,
                "spreadFactor": 0.2,
                "symmetryWeight": 0.85,
            }
        elif difficulty <= 0.7:
            self.boardConfig = {
                "initialState": InitialBoardState.PATTERN,
                "mutationsCount": randint(5, 9) * mutationsMultiplier,
                "spreadFactor": 0.65,
                "symmetryWeight": 0.4,
            }
        elif difficulty <= 0.9:
            self.boardConfig = {
                "initialState": InitialBoardState.PATTERN,
                "mutationsCount": randint(8, 12) * mutationsMultiplier,
                "spreadFactor": 0.8,
                "symmetryWeight": 0.1,
            }
        else:
            self.boardConfig = {
                "initialState": InitialBoardState.RANDOM,
                "mutationsCount": randint(10, 15) * mutationsMultiplier,
                "spreadFactor": 0.9,
                "symmetryWeight": 0,
            }

    def _generateBoards(self):
        self._setBoardConfig()

        self.targetBoard = Board(self.settings.boardSize, id="target")
        self.targetBoard.generateBase(self.boardConfig["initialState"])
        if self.settings.obstacles:
            self.targetBoard.addObstacles()

        self.playerBoard = self.targetBoard.toMutated(
            True,
            self.boardConfig["mutationsCount"],
            self.boardConfig["spreadFactor"],
            self.boardConfig["symmetryWeight"],
            "player",
        )

    def _handleInputOutcome(self, outcome: dict | None) -> bool:
        if outcome is not None:
            if outcome["moved"]:
                self.moves += 1
                self.sounds.play(SoundEffect.MOVE)
                return True
            elif outcome["flipped"]:
                self.flips += 1
                selectedPos = self.playerBoard.selectedPos
                if self.playerBoard[selectedPos] != self.targetBoard[selectedPos]:
                    self.mistakes += 1
                    if self.settings.suddenDeath:
                        self.isOver = self.didFatalMistake = True
                self.sounds.play(SoundEffect.INTERACT)
                return True
        return False

    def _getBoardOverrides(self, style: str, tile: str | tuple) -> dict:
        overrides = {}
        if isinstance(tile, tuple):
            overrides = {tile: style}
        elif tile == "selected":
            selectedPos = tuple(self.playerBoard.selectedPos)
            overrides = {selectedPos: style}
        elif tile == "all":
            overrides = {
                (i, j): style
                for j in range(self.settings.boardSize)
                for i in range(self.settings.boardSize)
            }
        return overrides

    def _drawRound(
        self, timeLeft: float = -1, boardSeparator: str = "", overrides: dict = {}
    ):
        width = ui.drawRoundHUD(self.roundNumber, timeLeft)
        ui.drawBoards(
            self.targetBoard,
            self.playerBoard,
            separator=boardSeparator,
            centerToWidth=width,
            overrides=overrides,
        )

    def _shouldBlinkFrame(self, eventTime: float, secondsBeforeEvent: float) -> bool:
        shouldBlink = False
        if eventTime:
            currentTime = perf_counter()
            timeUntilEvent = eventTime - currentTime
            if 0 < timeUntilEvent <= secondsBeforeEvent:
                shouldBlink = int(timeUntilEvent * 3) % 2 == 1
            else:
                shouldBlink = timeUntilEvent < 0
        return shouldBlink

    def _showFatalMistake(self):
        self.hideTargetBoard = False
        for i in range(5):
            doBlink = i % 2 == 0
            ui.clearConsole()
            boardOverrides = self._getBoardOverrides(
                "RED" if doBlink else "NONE", "selected"
            )
            self._drawRound(
                boardSeparator=" F A T A L " if doBlink else "",
                overrides=boardOverrides,
            )
            sleep(0.5)

    def _showRoundOver(self):
        roundStats = self._getFormattedStats()
        if self.didFatalMistake:
            self._showFatalMistake()
        else:
            for i in range(5):
                ui.clearConsole()
                if i % 2 == 0:
                    self._drawRound(
                        boardSeparator=(
                            " M A T C H " if self.won else " N O   M A T C H "
                        )
                    )
                else:
                    self._drawRound()
                sleep(0.5)
        sleep(0.5)
        width = ui.drawRoundHUD(self.roundNumber)
        ui.drawStatsSummary(roundStats, width)
        sleep(3)

    def _getFormattedStats(self) -> dict:
        stats = {
            "Tiempo": f"{round(self.timeElapsed, 2)}s",
            "Movimientos": self.moves,
            "Errores": self.mistakes,
        }
        return stats

    def start(self):
        clearActionQueue()
        self._generateBoards()
        self.player = Player(self.playerBoard, self.settings.inverseControls)
        startTime = lastRedrawTimer = lastChaosTimer = perf_counter()
        hideTargetTime = (
            startTime + self.settings.hideTargetAfter
            if self.settings.hideTargetAfter
            else None
        )
        chaosFlipTime = startTime + 3 if self.settings.chaosFlipping else None
        randomTile = self.playerBoard.getRandomPos()

        self._drawRound(self.settings.timeLimit if self.settings.timeLimit else -1)

        while not self.isOver:
            currentTime = perf_counter()
            needsRedraw = False
            overrides = {}

            if self.settings.chaosFlipping and currentTime - lastChaosTimer >= 3:
                lastChaosTimer = currentTime
                chaosFlipTime = currentTime + 3
                self.playerBoard.flipTile(randomTile)
                randomTile = self.playerBoard.getRandomPos()

            self.hideTargetBoard = self._shouldBlinkFrame(hideTargetTime, 2)
            doChaosFlipBlink = self._shouldBlinkFrame(chaosFlipTime, 2)

            if self.hideTargetBoard:
                overrides = {"target": self._getBoardOverrides("HIDDEN", "all")}
            if doChaosFlipBlink:
                overrides = {
                    **overrides,
                    "player": self._getBoardOverrides("GRAY", randomTile),
                }

            try:
                inputOutcome = self.player.handleInput()
                needsRedraw = self._handleInputOutcome(inputOutcome)
            except Empty:
                pass

            if (
                self.settings.timeLimit or self.settings.chaosFlipping
            ) and currentTime - lastRedrawTimer >= 0.1:
                lastRedrawTimer = currentTime
                needsRedraw = True

            if needsRedraw:
                elapsed = currentTime - startTime
                timeLeft = max(0, self.settings.timeLimit - elapsed)

                self._drawRound(
                    timeLeft if self.settings.timeLimit else -1, overrides=overrides
                )

                if self.won or self.settings.timeLimit and timeLeft <= 0:
                    self.isOver = True

        endTime = perf_counter()
        self.timeElapsed = endTime - startTime
        if self.settings.timeLimit and self.timeElapsed > self.settings.timeLimit:
            self.timeElapsed = self.settings.timeLimit

        self._showRoundOver()

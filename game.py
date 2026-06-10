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

    # Main menu
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

    # "Información" menu
    def handleAbout(self):
        ui.drawAbout()
        while True:
            action = getLatestAction()
            if action == "ESCAPE":
                break
        self.state = GameState.TITLE

    # "Configuración" menu
    def handleSettings(self):
        options = self.settings._generateOptionsList()
        numOptions = len(options)
        selected = 0

        while True:
            ui.drawSettings(options, selected)

            currentOption = options[selected]
            action = getLatestAction()

            # Menu navigation is done with UP and DOWN actions,
            # while per-setting toggling/adjusting is done with LEFT and RIGHT actions
            match action:
                case "UP":
                    selected = (selected - 1) % numOptions
                    self.sounds.play(SoundEffect.MOVE)
                case "DOWN":
                    selected = (selected + 1) % numOptions
                    self.sounds.play(SoundEffect.MOVE)
                case "LEFT" | "RIGHT":
                    # For number-based settings, cycle through each possible value
                    # according to their range and step
                    if currentOption["type"] in ["int", "time"]:
                        step = currentOption["step"]
                        currentOption["value"] = (
                            max(currentOption["value"] - step, currentOption["min"])
                            if action == "LEFT"
                            else min(
                                currentOption["value"] + step, currentOption["max"]
                            )
                        )
                    # For bool-based settings, simply toggle on or off
                    elif currentOption["type"] == "bool":
                        currentOption["value"] = action == "RIGHT"
                    # Make sure no setting values conflict with one another
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
        """Adjusts necessary game settings to avoid potential conflicts in the game loop.

        Args:
            options (list | tuple): List of options and their metadata.
            changedOption (dict): Last-changed option and its metadata.
        """
        match changedOption["id"]:
            # If timeLimit was just disabled (set to 0), disable hideTargetAfter if enabled
            case "timeLimit":
                if changedOption["value"] == 0:
                    for option in options:
                        if option["id"] == "hideTargetAfter" and option["value"] > 0:
                            option["value"] = 0
            # If hideTargetAfter was just enabled (set above 0), enable timeLimit and set to 30 if disabled
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
        # Start as many rounds as configured and record their stats
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
        # Calculate and store extra game-end statistics
        self.stats.calculateAccuracy()
        self.stats.calculateMPS()
        self.stats.calculateScore(self.settings)
        gameStatsSummary = self.stats.getFormattedStats()

        self.gameMusic.stop()
        self.sounds.play(SoundEffect.END)

        ui.clearConsole()
        ui.drawGameOver("resultados", gameStatsSummary)

        # Disable kbhit() bypass before each user input (i.e. force kbhit() check)
        setKbhitBypass(False)
        action = getLatestAction()
        if action == "ENTER":
            # Temporarily pause custom user-input listener to allow normal input() usage
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

            # Resume custom user-input listener
            unpauseActionListener()
            ui.hideCursor()

            playerData = self.getFormattedPlayerData(playerName)
            playerRankIdx = self.saveResults(playerData)
            # Set the leaderboard rank to be highlighted
            self.highlightLeaderboardIdx = playerRankIdx

            self.state = GameState.LEADERBOARD
        elif action == "ESCAPE":
            self.state = GameState.TITLE
        # Re-enable kbhit() bypass
        setKbhitBypass(True)

    def handleLeaderboard(self):
        lbData, _ = self.getLeaderboardData()

        ui.drawLeaderboard(lbData, self.highlightLeaderboardIdx)

        action = getLatestAction()
        if action == "ESCAPE":
            self.state = GameState.TITLE

    # Reads the leaderboard.json file
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

    # Writes new results to the leaderboard.json file
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
        """Sets the board configuration to be used during its mutation.

        Does so according a 'difficulty' parameter calculated linearly according to the current and total round(s).
        The configuration includes the initial state of the target board, as well as
        the mutation settings to be used for the player board.
        """
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

        # Create a new Board instance for the target board with the configuration's initial state
        self.targetBoard = Board(self.settings.boardSize, id="target")
        self.targetBoard.generateBase(self.boardConfig["initialState"])
        # Add obstacles to the target board if the game setting is enabled
        if self.settings.obstacles:
            self.targetBoard.addObstacles()

        # Create a new Board from the target board, mutated using the established configuration,
        # to be used as the player board
        self.playerBoard = self.targetBoard.toMutated(
            True,
            self.boardConfig["mutationsCount"],
            self.boardConfig["spreadFactor"],
            self.boardConfig["symmetryWeight"],
            "player",
        )

    def _handleInputOutcome(self, outcome: dict | None) -> bool:
        """Handles the outcome of the user's interaction with the board, such as keeping count of their moves and flips,
        playing sound effects, and checking against game-over conditions.

        Args:
            outcome (dict | None):
                Types of outcomes that emerged from the user input.
                Despite the use of plural, only one value out of each key, value pair may be True.

        Returns:
            bool: Whether an outcome 'happened' due to this user input (i.e. whether the player board has changed).
        """
        if outcome is not None:
            if outcome["moved"]:
                self.moves += 1
                self.sounds.play(SoundEffect.MOVE)
                return True
            elif outcome["flipped"]:
                self.flips += 1
                selectedPos = self.playerBoard.selectedPos
                # If the flipped tile in the player board does not align
                # with the same tile in the target board, count a mistake
                if self.playerBoard[selectedPos] != self.targetBoard[selectedPos]:
                    self.mistakes += 1
                    # If suddenDeath is enabled, mark round as over
                    if self.settings.suddenDeath:
                        self.isOver = self.didFatalMistake = True
                self.sounds.play(SoundEffect.INTERACT)
                return True
        return False

    def _getBoardOverrides(self, style: str, tile: str | tuple) -> dict:
        """Builds a dictionary specifying the style of one or all tiles via their positions in a board.

        Args:
            style (str):
                Style that the specified tiles will take. Refer to the ui module's _formattedTile function for possible styles.
            tile (str | tuple):
                Tile or tiles to apply the specified style to.
                May be the string 'selected' for the tile currently selected by the user, or 'all' for all tiles on the board.
                May be a tuple specifying the (i, j) position of a single tile.

        Returns:
            dict: Collection of tiles and their specified styles.
        """
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

    # Helper function used to mimic a blinking animation
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
        # Round setup; clear any user inputs waiting to be read, generate the target and player boards, and
        # set relevant variables associated with time-related events
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

            # If chaosFlipping is enabled, and enough time has passed since its last activation,
            # update its timer and flip a random tile in the player board
            if self.settings.chaosFlipping and currentTime - lastChaosTimer >= 3:
                lastChaosTimer = currentTime
                chaosFlipTime = currentTime + 3
                self.playerBoard.flipTile(randomTile)
                randomTile = self.playerBoard.getRandomPos()

            # Set whether the target board should alert the user whenever it is about to vanish,
            # since the timer is never updated, it will be hidden for the rest of the round
            # after its blinking animation is finished
            self.hideTargetBoard = self._shouldBlinkFrame(hideTargetTime, 2)
            doChaosFlipBlink = self._shouldBlinkFrame(chaosFlipTime, 2)

            # Hide target board once necessary (during blinking animation, and afterwards for remainder of the round)
            if self.hideTargetBoard:
                overrides = {"target": self._getBoardOverrides("HIDDEN", "all")}
            # Highlight previously-randomly-chosen tile that is about to flip on the next iteration,
            # in order to alert the user
            if doChaosFlipBlink:
                overrides = {
                    **overrides,
                    "player": self._getBoardOverrides("GRAY", randomTile),
                }

            # Attempt to retrieve the user's last input on the player board,
            # then set needsRedraw to a bool whether the player board actually changed
            try:
                inputOutcome = self.player.handleInput()
                needsRedraw = self._handleInputOutcome(inputOutcome)
            except Empty:
                pass

            # If timeLimit or chaosFlipping is enabled, and
            # more than 1/10th of a second has passed since the last redraw,
            # force one and update the timer
            if (
                self.settings.timeLimit or self.settings.chaosFlipping
            ) and currentTime - lastRedrawTimer >= 0.1:
                lastRedrawTimer = currentTime
                needsRedraw = True

            # Update time left for this round, redraw the screen, and check for win condition all only when needed
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

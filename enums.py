from enum import StrEnum, auto


class GameState(StrEnum):
    TITLE = auto()
    ABOUT = auto()
    SETTINGS = auto()
    PLAYING = auto()
    OVER = auto()
    LEADERBOARD = auto()
    QUIT = auto()


class InitialBoardState(StrEnum):
    BLANK = auto()
    PATTERN = auto()
    RANDOM = auto()

from enum import StrEnum, auto


class InitialBoardState(StrEnum):
    BLANK = auto()
    PATTERN = auto()
    RANDOM = auto()

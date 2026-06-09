"""
Module to store general enums.

This module stores enums vital to the game and board states as well as sound effects.

Contributors:
    - Herrera Armenta Emmanuel
"""

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


class SoundEffect(StrEnum):
    MOVE = auto()
    INTERACT = auto()
    GAME = auto()
    END = auto()

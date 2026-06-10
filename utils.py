"""
Module to define general utility functions.

This module defines functions vital to the user navigation and interaction process.

Contributors:
    - Herrera Armenta Emmanuel
"""

from dataclasses import field
from msvcrt import getch, kbhit
from queue import Queue, Empty
from threading import Thread, Event

_bypassKbhit = True
_actionQueue = Queue()
_runActionListenerFlag = Event()


def _getUserAction() -> str:
    """Converts user input into a predetermined action string.

    Returns:
        str: Word that describes the action being performed by the user.
    """
    inp = getch().lower()
    if inp in [b"\x00", b"\xe0"]:
        inp = getch()

    match inp:
        case b"w" | b"H":
            return "UP"
        case b"a" | b"K":
            return "LEFT"
        case b"s" | b"P":
            return "DOWN"
        case b"d" | b"M":
            return "RIGHT"
        case b"\r" | b" ":
            return "ENTER"
        case b"\x1b":
            return "ESCAPE"
        case _:
            return inp


# Custom user-input listener
def _globalActionListener():
    while True:
        # Wait until flag is set (i.e. pause listening if flag is unset)
        _runActionListenerFlag.wait()
        if _bypassKbhit or kbhit():
            # Get latest user action and place it into a queue
            action = _getUserAction()
            _actionQueue.put(action)


def pauseActionListener():
    _runActionListenerFlag.clear()


def unpauseActionListener():
    _runActionListenerFlag.set()


def setKbhitBypass(boolean: bool):
    global _bypassKbhit
    _bypassKbhit = boolean


def getLatestAction(timeout: float | None = None) -> str:
    return _actionQueue.get(timeout=timeout)


# Discard actions in the action queue until it's empty
def clearActionQueue():
    while not _actionQueue.empty():
        try:
            _actionQueue.get_nowait()
        except Empty:
            break


# Helper function to shorten the assignment of default values to dataclass attributes with mutable types
def defaultMutable(value):
    return field(default_factory=lambda: value)


# Start a single thread once so the custom user-input listener is always running
Thread(target=_globalActionListener, daemon=True).start()
unpauseActionListener()

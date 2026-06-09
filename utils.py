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


def _globalActionListener():
    while True:
        _runActionListenerFlag.wait()
        if _bypassKbhit or kbhit():
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


def clearActionQueue():
    while not _actionQueue.empty():
        try:
            _actionQueue.get_nowait()
        except Empty:
            break


def defaultMutable(value):
    return field(default_factory=lambda: value)


Thread(target=_globalActionListener, daemon=True).start()
unpauseActionListener()

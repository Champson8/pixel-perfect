from dataclasses import field
from msvcrt import getch
from queue import Queue
from threading import Thread


actionQueue = Queue()


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
        action = _getUserAction()
        actionQueue.put(action)


Thread(target=_globalActionListener, daemon=True).start()


def getLatestAction(timeout: float | None = None) -> str:
    return actionQueue.get(timeout=timeout)


def defaultMutable(value):
    return field(default_factory=lambda: value)

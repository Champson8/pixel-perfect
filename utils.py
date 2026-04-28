from dataclasses import field
from msvcrt import getch, kbhit
from queue import Queue, Empty
from threading import Thread


_actionQueue = Queue()


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
        if kbhit():
            action = _getUserAction()
            _actionQueue.put(action)


Thread(target=_globalActionListener, daemon=True).start()


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

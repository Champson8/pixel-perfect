from dataclasses import field
from sys import stdout
from msvcrt import getch


def getUserAction() -> str:
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


def defaultMutable(value):
    return field(default_factory=lambda: value)

from dataclasses import field
from sys import stdout
from msvcrt import getch
from colorama import Style


def getUserAction():
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


def overwriteConsole(message="\033[H\033[2J\033[3J"):
    stdout.write(message)
    stdout.flush()


def defaultMutable(value):
    return field(default_factory=lambda: value)


def resetStyleAfter(string):
    return string + Style.RESET_ALL


def rotateMatrixRight(m, iterations=1):
    for _ in range(iterations):
        m = list(map(list, zip(*m[::-1])))
    return m


def rotateMatrixLeft(m, iterations=1):
    for _ in range(iterations):
        m = list(map(list, zip(*m)))[::-1]
    return m

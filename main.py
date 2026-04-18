import time
from colorama import init
from board import Board
from utils import getUserAction, overwriteConsole
from constants import HIDE_CURSOR, TILE_CHARS, MOVES

init(autoreset=True)


overwriteConsole(HIDE_CURSOR)

board = Board(8, allowInteract=True)
board.generatePattern()

while True:
    overwriteConsole()
    overwriteConsole(str(board))
    board.player.interact(getUserAction())

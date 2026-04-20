import time
from colorama import init
from board import Board
from enums import InitialBoardState
from utils import getUserAction, overwriteConsole
from constants import HIDE_CURSOR

init(autoreset=True)


overwriteConsole(HIDE_CURSOR)

board = Board(6, allowInteract=True)
board.generateBase()

while True:
    overwriteConsole()
    overwriteConsole(str(board))
    board.player.interact(getUserAction())

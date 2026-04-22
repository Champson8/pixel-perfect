from colorama import init
from board import Board
from utils import getUserAction, overwriteConsole
from constants import HIDE_CURSOR

init(autoreset=True)


overwriteConsole(HIDE_CURSOR)

board = Board(4, allowInteract=True)
board.generateBase()

while True:
    overwriteConsole()
    overwriteConsole(str(board))
    board.player.interact(getUserAction())

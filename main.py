from colorama import init
import ui
from board import Board
from utils import getUserAction
from constants import HIDE_CURSOR


def main():
    init(autoreset=True)

    ui.overwriteConsole(HIDE_CURSOR)

    board = Board(4, allowInteract=True)
    board.generateBase()

    while True:
        ui.overwriteConsole()
        ui.drawBoard(board)
        board.player.interact(getUserAction())


if __name__ == "__main__":
    main()

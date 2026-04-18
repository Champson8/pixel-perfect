from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from constants import MOVES


if TYPE_CHECKING:
    from board import Board


@dataclass
class Player:
    board: Board

    def interact(self, action):
        tiles = self.board.tiles
        sel = self.board.selectedPos
        if action == "ENTER":
            currentTile = tiles[sel[0]][sel[1]]
            tiles[sel[0]][sel[1]] = int(not currentTile)
            return
        if action not in MOVES:
            return
        nextIPos = sel[0] + MOVES[action][0]
        nextJPos = sel[1] + MOVES[action][1]
        if (
            nextIPos < 0
            or nextJPos < 0
            or nextIPos + 1 > self.board.size
            or nextJPos + 1 > self.board.size
        ):
            return
        self.board.selectedPos = [nextIPos, nextJPos]

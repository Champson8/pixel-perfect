from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from board import Board


_MOVES = {"UP": [-1, 0], "LEFT": [0, -1], "DOWN": [1, 0], "RIGHT": [0, 1]}


@dataclass
class Player:
    board: Board

    def interact(self, action: str):
        sel = self.board.selectedPos
        if action == "ENTER":
            self.board.flipSelectedTile()
            return
        if action not in _MOVES:
            return
        nextIPos = sel[0] + _MOVES[action][0]
        nextJPos = sel[1] + _MOVES[action][1]
        if (
            nextIPos < 0
            or nextJPos < 0
            or nextIPos + 1 > self.board.size
            or nextJPos + 1 > self.board.size
        ):
            return
        self.board.moveSelection(nextIPos, nextJPos)

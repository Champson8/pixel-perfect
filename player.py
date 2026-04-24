from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from utils import getUserAction

if TYPE_CHECKING:
    from board import Board


_MOVES = {"UP": [-1, 0], "LEFT": [0, -1], "DOWN": [1, 0], "RIGHT": [0, 1]}


@dataclass
class Player:
    linkedBoard: Board

    def handleInput(self) -> dict | None:
        outcome = {"moved": False, "flipped": False}
        sel = self.linkedBoard.selectedPos
        action = getUserAction()

        if action == "ENTER":
            self.linkedBoard.flipSelectedTile()
            outcome["flipped"] = True
            return outcome

        if action not in _MOVES:
            return None

        nextIPos = sel[0] + _MOVES[action][0]
        nextJPos = sel[1] + _MOVES[action][1]
        if (
            nextIPos < 0
            or nextJPos < 0
            or nextIPos + 1 > self.linkedBoard.size
            or nextJPos + 1 > self.linkedBoard.size
        ):
            return None

        self.linkedBoard.moveSelection(nextIPos, nextJPos)
        outcome["moved"] = True
        return outcome

"""
Module to handle in-game-loop player interaction.

This module handles player input and movement once inside a game loop.

Contributors:
    - Herrera Armenta Emmanuel
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING
from utils import getLatestAction

if TYPE_CHECKING:
    from board import Board


_MOVES = {"UP": [-1, 0], "LEFT": [0, -1], "DOWN": [1, 0], "RIGHT": [0, 1]}


@dataclass
class Player:
    linkedBoard: Board
    invertControls: bool = False

    def _getMoves(self) -> dict[str, list]:
        moves = deepcopy(_MOVES)
        if self.invertControls:
            moves["UP"], moves["DOWN"] = moves["DOWN"], moves["UP"]
            moves["LEFT"], moves["RIGHT"] = moves["RIGHT"], moves["LEFT"]
        return moves

    def handleInput(self) -> dict | None:
        outcome = {"moved": False, "flipped": False}
        sel = self.linkedBoard.selectedPos
        moves = self._getMoves()
        action = getLatestAction(0.1)

        if action == "ENTER":
            self.linkedBoard.flipSelectedTile()
            outcome["flipped"] = True
            return outcome

        if action not in moves:
            return None

        nextIPos = sel[0] + moves[action][0]
        nextJPos = sel[1] + moves[action][1]
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

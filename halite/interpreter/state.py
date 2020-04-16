"""
This module defines the game.
"""

from itertools import count

from halite.utils import RepresentationMixin, setup_logger
from halite.interpreter.player import Player
from halite.interpreter.unit import Ship, Shipyard


_UID = count()
_LOGGER = setup_logger(__name__)


class State(RepresentationMixin):
    """
    A game state that keeps track of the board map, the steps, the units and the halite.

    Args:
        board_cells (halite.interpreter.board.BoardCell): The board cells.
        step (int): The current game round.
        units (dict[halite.interpreter.unit._Unit]): The units.
        halite_score (list[float]): The halite per player.
        halite_board (list[float]): The halite per cell on the board.
    """

    def __init__(self, *, step, units, halite_score, halite_board):
        self._step = step
        self._units = units
        self._halite_score = halite_score
        self._halite_board = halite_board

    def create_uid(self):
        return f"{self.step}-{next(_UID)}"

    @property
    def step(self):
        return self._step

    @property
    def halite_score(self):
        return self._halite_score

    @property
    def halite_board(self):
        return self._halite_board

    @property
    def units(self):
        return self._units

    def filter_units(self, player=None, class_=None, status=None):
        def filter_(unit):
            if player is not None and unit[1].player != player:
                return False
            if class_ is not None and not isinstance(unit[1], class_):
                return False
            if status is not None and unit[1].status != status:
                return False
            return True

        return filter(filter_, self._units.items())

    def ships(self, player=None, status=None):
        return self.units(class_=Ship, player=player, status=status)

    def shipyards(self, player=None, status=None):
        return self.units(class_=Shipyard, player=player, status=status)

    @property
    def _repr_attrs(self):
        return {
            "step": self.step,
            "units": self.units,
            "halite_score": self.halite_score,
            "halite_board_sum": sum(self.halite_board),
        }

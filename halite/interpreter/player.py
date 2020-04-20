"""
This module defines the player that plays the game.
"""

from halite.interpreter.constants import UnitStatus
from halite.utils import RepresentationMixin, merge_dicts, merge_lists


class Player(RepresentationMixin):
    """
    A player for the game.

    Args:
        index (int): The index of the player.
        game (halite.interpreter.game.Game): The game the player plays.
    """

    def __init__(self, *, index, game):
        self._index = index
        self._game = game

    @property
    def index(self):
        """
        The index of the player.
        """
        return self._index

    @property
    def game(self):
        """
        The game the player plays.
        """
        return self._game

    @property
    def halite(self):
        return self._game.halite_score[self.index]

    @property
    def units(self):
        return self.game.units(player=self, status=UnitStatus.ACTIVE)

    @property
    def ships(self):
        return self.game.ships(player=self, status=UnitStatus.ACTIVE)

    @property
    def shipyards(self):
        return self.game.shipyards(player=self, status=UnitStatus.ACTIVE)

    @property
    def spawn_log(self):
        """
        A log of all ships that the player spawned.
        """
        return merge_lists([shipyard.spawn_log for shipyard in self.shipyards.values()])

    @property
    def deposit_log(self):
        """
        A log of all halite that the player deposited.
        """
        return merge_lists(
            [shipyard.deposit_log for shipyard in self.shipyards.values()]
        )

    @property
    def _repr_attrs(self):
        return {
            "index": self.index,
            "halite": self.halite,
            "ships": list(dict(self.ships).values()),
            "shipyards": list(dict(self.shipyards).values()),
        }

"""
This module defines the player that plays the game.
"""

from halite.utils import RepresentationMixin, merge_dicts, merge_lists


class Player(RepresentationMixin):
    """
    A player for the game.

    Args:
        index (int): The index of the player.
        halite (int): The amount of halite the player owns.
        shipyards (dict[halite.interpreter.unit.Shipyard]): The dict of shipyards the
            player ownsn.
        ships (dict[halite.interpreter.unit.Ship]): The dict of ships the player owns.
        game (halite.interpreter.game.Game): The game the player plays.
    """

    def __init__(self, *, index, halite, shipyards, ships, game):
        self._index = index
        self.halite = halite
        self.shipyards = shipyards
        self.ships = ships
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
    def units(self):
        """
        All units (shipyards and ships) that the player owns.
        """
        return merge_dicts([self.shipyards, self.ships])

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

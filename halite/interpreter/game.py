"""
This module defines the game.
"""

import operator

from halite.utils import RepresentationMixin, merge_dicts, setup_logger
from halite.interpreter.unit import Ship, Shipyard


_LOGGER = setup_logger(__name__)


class Game(RepresentationMixin):
    """
    A game that has control over the configuration, the players and the board map.

    Args:
        configuration (halite.interpreter.configuration.Configuration): The
            configuration.
        players (list[halite.interpreter.player.Player]): The players.
        board_map (halite.interpreter.board_map.BoardMap): The board map.
        step (int): The current game round.
    """

    def __init__(self, configuration, players, board_map, step):
        self.configuration = configuration
        self.players = players
        self.board_map = board_map
        self.step = step

    def _units(self, attr):
        return merge_dicts([getattr(player, attr) for player in self.players])

    @property
    def ships(self):
        """
        The ships of all players in the game.
        """
        return self._units("ships")

    @property
    def shipyards(self):
        """
        The shipyards of all players in the game.
        """
        return self._units("shipyards")

    @property
    def units(self):
        """
        The units of all players in the game.
        """
        return self._units("units")

    def detect_collision(self):
        """
        Detects collision between units.
        First detects collisions between ships and enemy shipyards.
        Then detects collision between multiple ships.
        """

        def detect_collision_with_shipyards(self):
            for ship in self.ships.values():
                enemy_shipyards = [
                    unit
                    for unit in ship.occupies.occupied_by
                    if isinstance(unit, Shipyard) and unit.player != ship.player
                ]
                if enemy_shipyards:
                    _LOGGER.info(
                        f"Collision detected between {ship} and {enemy_shipyards[0]}."
                    )
                    ship.destroy()

        def detect_collision_between_ships(self):
            for board_cell in self.board_map:
                ships = [
                    unit for unit in board_cell.occupied_by if isinstance(unit, Ship)
                ]
                if len(ships) <= 1:
                    continue
                ships.sort(key=operator.attrgetter("halite"), reverse=True)
                collision_str = ", ".join(str(ship) for ship in ships)
                _LOGGER.info(f"Collision detected between {collision_str}.")
                second_largest_halite = ships[1].halite
                for ship in ships[1:]:
                    ship.destroy()
                if ships[0].halite == second_largest_halite:
                    ships[0].destroy()
                else:
                    ships[0].damage(second_largest_halite)
                board_cell.destroy()

        detect_collision_with_shipyards(self)
        detect_collision_between_ships(self)

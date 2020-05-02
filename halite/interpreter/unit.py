"""
This module provides the two units in this game: Ships and shipyards.
"""

from abc import ABC
import pdb

from halite.utils import RepresentationMixin
from halite.interpreter.state import UnitState
from halite.interpreter.constants import UnitStatus


class _Unit(RepresentationMixin, ABC):

    _UNIT_TYPE = None

    def __init__(self, uid, game):
        self._uid = uid
        self._game = game

    @property
    def uid(self):
        return self._uid

    @property
    def game(self):
        return self._game

    @property
    def _state(self):
        state = self.game.state.unit_states[self.uid]
        try:
            if self._UNIT_TYPE and self._UNIT_TYPE != state.unit_type:
                raise IncorrectUnitType
        except AttributeError:
            pdb.set_trace()
        return state

    @property
    def pos(self):
        return self._state.pos

    @property
    def player(self):
        return self.game.players[self._state.player_index]

    @property
    def created_at(self):
        """
        The step the unit was created in.
        """
        return self._state.created_at

    @property
    def status(self):
        """
        The status of the unit.
        """
        return self._state.unit_status

    @property
    def occupies(self):
        """
        The cell that is occupied by this unit.

        Returns:
            halite.interpreter.board.BoardCell: The occupied cell.
        """
        return self._game.board[self.pos]

    @property
    def _repr_attrs(self):
        repr_attrs = {
            "uid": self.uid,
            "pos": self.pos,
            "created_at": self.created_at,
            "status": self.status,
            "player_index": self.player.index,
        }
        if self.status != UnitStatus.ACTIVE:
            repr_attrs = {
                **repr_attrs,
                "deleted_at": self.deleted_at,
            }
        return repr_attrs


class Shipyard(_Unit):

    _UNIT_TYPE = "SHIPYARD"
    """
    A shipyard that can spawn ships and can deposit halite from ships.

    Args:

        uid (str): The uid.
        pos (int): The position.
        player (halite.interpreter.player.Player): The player that controls the unit.
        created_at (int): The step in which the unit was created.
        converted_from (halite.interpreter.unit.Ship): The ship that this shipyard was
            converted from.
        spawned_ships (list, optional): The list of ships that were spawned from this
            shipyard.
        deposit_log (list, optional): The list of dicts that describe all deposits to
            this shipyard.
    """

    @property
    def converted_from(self):
        """
        The ship this shipyard was converted from.
        """
        return self._game.units[self._state.converted_from_uid]

    @property
    def spawned_ships(self):
        """
        The ships that were spawned from this shipyard.
        """
        for uid in self.state.spawned_ship_uid:
            yield self._game.units[uid]


class Ship(_Unit):
    _UNIT_TYPE = "SHIP"
    """
    A ship that can mine halite and deposit it at a shipyard.
    """

    @property
    def halite(self):
        """
        The amount of halite in the ship.
        """
        return self._state.halite

    @property
    def converted_to(self):
        """
        The shipyard this ship was converted to.
        """
        return self._game.units[self._state.converted_to_uid]

    @property
    def spawned_from(self):
        """
        This shipyard this ship was spawned from.
        """
        return self._game.units[self._state.spawned_from_uid]

    @property
    def occupied_friendly_shipyard(self):
        """
        Whether the ship is currently occupying a friendly shipyard.
        """
        for unit in self.occupies.occupied_by:
            if unit.player == self.player and isinstance(unit, Shipyard):
                return unit
        return None

    @property
    def _repr_attrs(self):
        repr_attrs = {**super()._repr_attrs, "halite": self.halite}
        if self.status == UnitStatus.CONVERTED:
            repr_attrs = {**repr_attrs, "converted_to": self.converted_to}
        return repr_attrs

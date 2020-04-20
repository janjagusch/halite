"""
This module provides the two units in this game: Ships and shipyards.
"""

from abc import ABC

from halite.utils import RepresentationMixin, setup_logger
from halite.interpreter.exceptions import (
    CantConvertError,
    InactiveUnitError,
    CantSpawnError,
    CantDepositError,
)
from halite.interpreter.state import UnitState
from halite.interpreter.constants import UnitStatus


_LOGGER = setup_logger(__name__)


class _Unit(RepresentationMixin, ABC):
    """
    Abstract parent class of units.

    Args:

        uid (str): The uid.
        pos (int): The position.
        player (halite.interpreter.player.Player): The player that controls the unit.
        created_at (int): The step in which the unit was created.
        status (str, optional): The status of the unit
            (active, converted or destroyed).
        deleted_at (int, optional): The step in which the unit was deleted
            (converted or destroyed).
    """

    def __init__(self, *, game, state):
        self._game = game
        self.state = state

    @property
    def uid(self):
        """
        The uid of the unit.
        """
        return self.state.uid

    @property
    def pos(self):
        """
        The position of the unit.
        """
        return self.state.pos

    @property
    def player(self):
        """
        The player that owns the unit.
        """
        return self._game.players[self.state.player_index]

    @property
    def created_at(self):
        """
        The step the unit was created in.
        """
        return self.state.created_at

    @property
    def status(self):
        """
        The status of the unit.
        """
        return self.state.unit_status

    @property
    def deleted_at(self):
        """
        The step the unit was deleted in.
        """
        return self.state.deleted_at

    @property
    def _logging_prefix(self):
        return (
            f"Player {self.player.index}'s {self.__class__.__name__.lower()} {self.uid}"
        )

    @property
    def _configuration(self):
        return self._game.configuration

    @property
    def occupies(self):
        """
        The cell that is occupied by this unit.

        Returns:
            halite.interpreter.board.BoardCell: The occupied cell.
        """
        return self._game.board[self.pos]

    @property
    def _step(self):
        return self._game.step

    def _assert_is_active(self):
        if self.status != UnitStatus.ACTIVE:
            raise InactiveUnitError(self.uid)

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
        return self._game.units[self.state.converted_from_uid]

    @property
    def spawned_ships(self):
        """
        The ships that were spawned from this shipyard.
        """
        for uid in self.state.spawned_ship_uid:
            yield self._game.units[uid]

    @property
    def deposit_log(self):
        """
        The log of all halite deposited in this shipyard.
        """
        return self.state.deposit_log

    @property
    def _spawn_cost(self):
        return self._configuration.spawn_cost

    @property
    def spawn_log(self):
        """
        The log of all ships spawned from this shipyard.
        """
        return [
            {"step": ship.created_at, "shipyard_uid": self.uid, "ship_uid": ship.uid,}
            for ship in self.spawned_ships.values()
        ]

    def deposit(self, ship):
        """
        Deposits the halite of a ship.

        Args:
            ship (halite.interpreter.unit.Ship): The ship that wants to deposit halite.
        """
        self._assert_is_active()
        self.state.deposit_log.append(
            {
                "step": self._step,
                "shipyard_uid": self.uid,
                "ship_uid": ship.uid,
                "amount": ship.halite,
            }
        )
        _LOGGER.info(
            f"{self._logging_prefix} received a deposit of {ship.halite} halite "
            f"from ship {ship.uid}."
        )

    def spawn(self, uid):
        """
        Spawns a new ship.

        Returns:
            halite.interpreter.unit.Ship: The new ship.

        Raises:
            CantSpawnError: When you cannot spawn a ship.
        """
        self._assert_is_active()
        if self.player.halite < self._spawn_cost:
            raise CantSpawnError("Insufficient halite.")

        ship = Ship(
            game=self._game,
            state=UnitState.create_ship(
                uid=uid,
                pos=self.pos,
                player_index=self.player.index,
                created_at=self._step,
                spawned_from_uid=self.uid, 
            )
        )

        self.state.spawned_ship_uids[ship.uid] = ship

        _LOGGER.info(
            f"{self._logging_prefix} spawned ship {ship.uid} at cell {self.pos}."
        )

        return ship, self._spawn_cost


class Ship(_Unit):
    """
    A ship that can mine halite and deposit it at a shipyard.
    """

    @property
    def halite(self):
        """
        The amount of halite in the ship.
        """
        return self.state.halite

    @property
    def converted_to(self):
        """
        The shipyard this ship was converted to.
        """
        return self._game.units[self.state.converted_to_uid]

    @property
    def spawned_from(self):
        """
        This shipyard this ship was spawned from.
        """
        return self._game.units[self.state.spawned_from_uid]

    def move(self, direction):
        """
        Moves a ship into a direction.

        Args:
            direction (str): The direction ("NORTH", "EAST", "SOUTH", "WEST").
        """
        self._assert_is_active()
        self.state.halite *= 1 - self._configuration.move_cost
        self.state.pos = self.occupies.neighbour(direction).pos
        _LOGGER.info(
            f"{self._logging_prefix} moved {direction.lower()}wards to cell {self.pos}."
        )

    def mine(self):
        """
        Mines halite on the currently occupied cell.
        """
        self._assert_is_active()
        mined_halite = self.occupies.mine()
        self.state.halite += mined_halite
        _LOGGER.info(
            f"{self._logging_prefix} mined {mined_halite} "
            f"halite from cell {self.pos}."
        )

    @property
    def _convert_cost(self):
        return self._configuration.convert_cost

    def _delete(self, status):
        self.state.halite = None
        self.state.pos = None
        self.state.status = status
        self.state.deleted_at = self._step

    def convert(self, uid):
        """
        Converts the ship into a shipyard at the currently occupied cell.

        Returns:
            halite.interpreter.unit.Shipyard: The converted shipyard.

        Raises:
            CantConvertError: When you cannot convert the ship to a shipyard.
        """
        self._assert_is_active()
        if self.player.halite < self._convert_cost - self.halite:
            raise CantConvertError("Insufficient halite.")
        if any(self.pos == shipyard.pos for _, shipyard in self.player.shipyards):
            raise CantConvertError("Shipyard already present.")

        shipyard = Shipyard(
            game=self._game,
            state=UnitState.create_shipyard(
                uid=uid,
                pos=self.pos,
                player_index=self.player_index,
                created_at=self._step,
                converted_from_uid=self.uid,
            )
        )

        cost = int(self._convert_cost - self.halite)

        _LOGGER.info(
            f"{self._logging_prefix} was converted into " f"shipyard {shipyard.uid}."
        )
        self.occupies.convert()

        self._delete(UnitStatus.CONVERTED)
        self._converted_to = shipyard

        return shipyard, cost

    def deposit(self):
        """
        Deposits halite at the friendly shipyard at the currently occupied cell.
        """
        self._assert_is_active()
        shipyards = [
            unit
            for unit in self.occupies.occupied_by
            if unit.player == self.player and isinstance(unit, Shipyard)
        ]
        if not shipyards:
            raise CantDepositError("Not over a friendly shipyard.")
        shipyard = shipyards[0]
        _LOGGER.info(
            f"{self._logging_prefix} deposited {self.halite} "
            f"halite at shipyard {shipyard.uid}."
        )
        shipyard.deposit(self)

        halite = self.halite
        self.state.halite = 0
        return halite

    def destroy(self):
        """
        Destroys the ship.
        """
        self._assert_is_active()
        _LOGGER.info(f"Oh no! {self._logging_prefix} was destroyed!")
        self._delete(UnitStatus.DESTROYED)

    def damage(self, amount):
        """
        Damages the ship so that it looses halite.

        Args:
            amount (int): The amount of halite lost.
        """
        self._assert_is_active()
        _LOGGER.info(
            f"Oh no! {self._logging_prefix} was damaged and " f"lost {amount} halite!"
        )
        self.state.halite -= amount

    @property
    def _repr_attrs(self):
        repr_attrs = {**super()._repr_attrs, "halite": self.halite}
        if self.status == UnitStatus.CONVERTED:
            repr_attrs = {**repr_attrs, "converted_to": self.converted_to}
        return repr_attrs

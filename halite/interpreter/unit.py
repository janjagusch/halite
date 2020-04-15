"""
This module provides the two units in this game: Ships and shipyards.
"""

from abc import ABC
from itertools import count

from halite.utils import RepresentationMixin, setup_logger
from halite.interpreter.exceptions import (
    CantConvertError,
    InactiveUnitError,
    CantSpawnError,
    CantDepositError,
)


_LOGGER = setup_logger(__name__)
_UID = count()


def _create_uid(step):
    return f"{step}-{next(_UID)}"


class _Status:

    ACTIVE = "ACTIVE"
    DESTROYED = "DESTROYED"
    CONVERTED = "CONVERTED"


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

    def __init__(self, *, uid, pos, player, created_at, status=None, deleted_at=None):
        self._uid = uid
        self._pos = pos
        self._player = player
        self._created_at = created_at
        self._status = status or _Status.ACTIVE
        self._deleted_at = deleted_at

    @property
    def uid(self):
        """
        The uid of the unit.
        """
        return self._uid

    @property
    def pos(self):
        """
        The position of the unit.
        """
        return self._pos

    @property
    def player(self):
        """
        The player that owns the unit.
        """
        return self._player

    @property
    def created_at(self):
        """
        The step the unit was created in.
        """
        return self._created_at

    @property
    def status(self):
        """
        The status of the unit.
        """
        return self._status

    @property
    def deleted_at(self):
        """
        The step the unit was deleted in.
        """
        return self._deleted_at

    @property
    def _logging_prefix(self):
        return (
            f"Player {self.player.index}'s {self.__class__.__name__.lower()} {self.uid}"
        )

    @property
    def _game(self):
        return self.player.game

    @property
    def _configuration(self):
        return self._game.configuration

    @property
    def occupies(self):
        """
        The cell that is occupied by this unit.

        Returns:
            halite.interpreter.board_map.BoardCell: The occupied cell.
        """
        return self._game.board_map[self.pos]

    @property
    def _step(self):
        return self._game.step

    def _assert_is_active(self):
        if self.status != _Status.ACTIVE:
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
        if self.status != _Status.ACTIVE:
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

    def __init__(
        self,
        *,
        uid,
        pos,
        player,
        created_at,
        converted_from,
        spawned_ships=None,
        deposit_log=None,
    ):
        super().__init__(
            uid=uid,
            pos=pos,
            player=player,
            created_at=created_at,
            status=_Status.ACTIVE,
            deleted_at=None,
        )
        self._converted_from = converted_from
        self._spawned_ships = spawned_ships or {}
        self._deposit_log = deposit_log or []

    @property
    def converted_from(self):
        """
        The ship this shipyard was converted from.
        """
        return self._converted_from

    @property
    def spawned_ships(self):
        """
        The ships that were spawned from this shipyard.
        """
        return self._spawned_ships

    @property
    def deposit_log(self):
        """
        The log of all halite deposited in this shipyard.
        """
        return self._deposit_log

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
        self.player.halite += ship.halite
        self._deposit_log.append(
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

    def spawn(self):
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
            uid=_create_uid(self._step),
            pos=self.pos,
            player=self.player,
            halite=0,
            created_at=self._step,
            status=_Status.ACTIVE,
            deleted_at=None,
            converted_to=None,
            spawned_from=self,
        )
        self.player.ships[ship.uid] = ship
        self._spawned_ships[ship.uid] = ship

        self.player.halite -= self._spawn_cost

        _LOGGER.info(
            f"{self._logging_prefix} spawned ship {ship.uid} at cell {self.pos}."
        )

        return ship


class Ship(_Unit):
    """
    A ship that can mine halite and deposit it at a shipyard.

    Args:
        uid (str): The uid.
        pos (int): The position.
        player (halite.interpreter.player.Player): The player that controls the unit.
        created_at (int): The step in which the unit was created.
        status (str, optional): The status of the unit
            (active, converted or destroyed).
        deleted_at (int, optional): The step in which the unit was deleted
            (converted or destroyed).
        halite (int): The amount of halite inside the ship.
        converted_to (halite.interpreter.unit.Shipyard): The shipyard this ship was
            converted to.
        spawned_from (halite.interpreter.unit.Shipyard): The shipyard that spawned this
            ship.
    """

    def __init__(
        self,
        *,
        uid,
        pos,
        player,
        created_at,
        halite,
        status=None,
        deleted_at=None,
        converted_to=None,
        spawned_from=None,
    ):
        super().__init__(
            uid=uid,
            pos=pos,
            player=player,
            created_at=created_at,
            status=status,
            deleted_at=deleted_at,
        )
        self._halite = halite
        self._converted_to = converted_to
        self._spawned_from = spawned_from

    @property
    def halite(self):
        """
        The amount of halite in the ship.
        """
        return self._halite

    @property
    def converted_to(self):
        """
        The shipyard this ship was converted to.
        """
        return self._converted_to

    @property
    def spawned_from(self):
        """
        This shipyard this ship was spawned from.
        """
        return self._spawned_from

    def move(self, direction):
        """
        Moves a ship into a direction.

        Args:
            direction (str): The direction ("NORTH", "EAST", "SOUTH", "WEST").
        """
        self._assert_is_active()
        self._halite *= 1 - self._configuration.move_cost
        self._pos = self.occupies.neighbour(direction).pos
        _LOGGER.info(
            f"{self._logging_prefix} moved {direction.lower()}wards to cell {self.pos}."
        )

    def mine(self):
        """
        Mines halite on the currently occupied cell.
        """
        self._assert_is_active()
        mined_halite = self.occupies.mine()
        self._halite += mined_halite
        _LOGGER.info(
            f"{self._logging_prefix} mined {mined_halite} "
            f"halite from cell {self.pos}."
        )

    @property
    def _convert_cost(self):
        return self._configuration.convert_cost

    def _delete(self, status):
        self._halite = None
        self._pos = None
        self._status = status
        self._deleted_at = self._step
        del self.player.ships[self.uid]

    def convert(self):
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
        if any(self.pos == shipyard.pos for shipyard in self.player.shipyards.values()):
            raise CantConvertError("Shipyard already present.")

        shipyard = Shipyard(
            uid=_create_uid(self._step),
            pos=self.pos,
            player=self.player,
            created_at=self._step,
            converted_from=self,
        )
        self.player.shipyards[shipyard.uid] = shipyard
        self.player.halite -= int(self._convert_cost - self.halite)

        _LOGGER.info(
            f"{self._logging_prefix} was converted into " f"shipyard {shipyard.uid}."
        )
        self.occupies.convert()

        self._delete(_Status.CONVERTED)
        self._converted_to = shipyard

        return shipyard

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
        self._halite = 0

    def destroy(self):
        """
        Destroys the ship.
        """
        self._assert_is_active()
        _LOGGER.info(f"Oh no! {self._logging_prefix} was destroyed!")
        self._delete(_Status.DESTROYED)

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
        self._halite -= amount

    @property
    def _repr_attrs(self):
        repr_attrs = {**super()._repr_attrs, "halite": self.halite}
        if self.status == _Status.CONVERTED:
            repr_attrs = {**repr_attrs, "converted_to": self.converted_to}
        return repr_attrs

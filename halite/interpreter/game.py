"""
This module defines the game.
"""

from contextlib import contextmanager
from random import randint
from uuid import uuid4
import copy
import operator
import math

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

from halite.utils import RepresentationMixin, merge_dicts
from halite.interpreter.exceptions import (
    CantSpawn,
    CantConvert,
    CantDeposit,
    ImpossibleAction,
    IllegalAction,
    InvalidUnitError,
    NoStateError,
)
from halite.interpreter.board import Board
from halite.interpreter.player import Player
from halite.interpreter.unit import Ship, Shipyard
from halite.interpreter.constants import UnitStatus, Actions, Events
from halite.interpreter.state import State, UnitState, UnitType


_LOGGER = structlog.get_logger(__name__)


class Game(RepresentationMixin):
    """
    A game that has control over the configuration, the players and the board map.

    Args:
        configuration (halite.interpreter.configuration.Configuration): The
            configuration.
        players (list[halite.interpreter.player.Player]): The players.
        board (halite.interpreter.board.Board): The board.
        step (int): The current game round.
    """

    def __init__(self, *, configuration, n_players=4, starting_halite=5000, uuid=None):
        self._configuration = configuration
        self._players = [self._create_player(index) for index in range(n_players)]
        self._board = Board(game=self)
        self._starting_halite = starting_halite
        self._state = None
        self._units = None
        self._uuid = uuid or uuid4().hex

    @contextmanager
    def load_state(self, state):
        def _load_unit(self, state):
            UnitType.assert_valid(state.unit_type)
            if state.unit_type == UnitType.SHIP:
                return Ship(uid=state.uid, game=self)
            elif state.unit_type == UnitType.SHIPYARD:
                return Shipyard(uid=state.uid, game=self)

        state = copy.deepcopy(state)
        try:
            self._state = state
            self._units = {
                uid: _load_unit(self, unit_state)
                for uid, unit_state in state.unit_states.items()
            }
            yield self
        finally:
            self._state = None
            self._units = None

    @property
    def n_players(self):
        return len(self.players)

    @property
    def starting_halite(self):
        return self._starting_halite

    def _create_uid(self):
        return self.state.create_uid()

    @property
    def players(self):
        return self._players

    @property
    def configuration(self):
        return self._configuration

    @property
    def board(self):
        return self._board

    @property
    def state(self):
        if not self._state:
            raise NoStateError
        return self._state

    @property
    def halite_score(self):
        return self.state.halite_score

    @property
    def board(self):
        return self._board

    def _filter_units(self, player=None, class_=None, status=None):
        def _filter(unit):
            if player is not None and unit.player != player:
                return False
            if class_ is not None and not isinstance(unit, class_):
                return False
            if status is not None and unit.status != status:
                return False
            return True

        return filter(lambda item: _filter(item[1]), self._units.items())

    def units(self, player=None, class_=None, status=None):
        return self._filter_units(player=player, class_=class_, status=status)

    def ships(self, player=None, status=None):
        return self.units(class_=Ship, player=player, status=status)

    def shipyards(self, player=None, status=None):
        return self.units(class_=Shipyard, player=player, status=status)

    def _detect_collision(self):
        """
        Detects collision between units.
        First detects collisions between ships and enemy shipyards.
        Then detects collision between multiple ships.
        """

        def destroy_ship(self, ship):
            _LOGGER.info(
                "",
                event_type=Events.DESTROYED,
                ship_uid=ship.uid,
                halite=-ship.halite,
                pos=ship.pos,
                player_index=ship.player.index,
            )
            self._delete_ship(ship, UnitStatus.DESTROYED)

        def damage_ship(self, ship, damage):
            _LOGGER.info(
                "",
                event_type=Events.DAMAGED,
                ship_uid=ship.uid,
                halite=-damage,
                pos=ship.pos,
                player_index=ship.player.index,
            )
            self._state.unit_states[ship.uid].halite -= damage

        def destroy_board_cell(self, board_cell):
            # TODO: Add logging.
            self._deplete_board_cell(board_cell)

        def detect_collision_with_shipyards(self):
            for _, ship in self.ships(status=UnitStatus.ACTIVE):
                enemy_shipyard = None
                for unit in ship.occupies.occupied_by:
                    if isinstance(unit, Shipyard) and unit.player != ship.player:
                        enemy_shipyard = unit
                        break
                if enemy_shipyard:
                    _LOGGER.info(
                        f"Collision detected between {ship} and {enemy_shipyard}."
                    )
                    destroy_ship(self, ship)

        def detect_collision_between_ships(self):
            for board_cell in self.board:
                ships = list(
                    unit for unit in board_cell.occupied_by if isinstance(unit, Ship)
                )
                if len(ships) <= 1:
                    continue
                ships.sort(key=operator.attrgetter("halite"), reverse=True)
                collision_str = ", ".join(str(ship) for ship in ships)
                _LOGGER.info(f"Collision detected between {collision_str}.")
                second_largest_halite = ships[1].halite
                for ship in ships[1:]:
                    destroy_ship(self, ship)
                if ships[0].halite == second_largest_halite:
                    destroy_ship(self, ships[0])
                else:
                    damage_ship(self, ships[0], second_largest_halite)
                destroy_board_cell(self, board_cell)

        detect_collision_with_shipyards(self)
        detect_collision_between_ships(self)

    def _delete_ship(self, ship, status):
        state = self._state.unit_states[ship.uid]
        state.halite = None
        state.pos = None
        state.unit_status = status
        state.deleted_at = self._state.step

    def _deplete_board_cell(self, board_cell):
        self._state.halite_board[board_cell.pos] = 0

    @staticmethod
    def _assert_valid_action(player, unit, required_unit_class):
        assert player == unit.player
        assert isinstance(unit, required_unit_class)
        if unit.status != UnitStatus.ACTIVE:
            raise InactiveUnitError(unit.uid)

    def _spawn(self, player, shipyard):
        self._assert_valid_action(player, shipyard, Shipyard)

        cost = self.configuration.spawn_cost

        if player.halite < cost:
            raise CantSpawn("Insufficient halite.")

        self._state.halite_score[shipyard.player.index] -= cost
        ship = self._create_ship(
            pos=shipyard.pos, player=shipyard.player, spawned_from=shipyard
        )

        _LOGGER.info(
            "", event_type=Events.SPAWNED, ship_uid=ship.uid, shipyard_uid=shipyard.uid
        )

    def _convert(self, player, ship):
        def convert_ship(self, ship, shipyard):
            # TODO: Add logging
            state = self._state.unit_states[ship.uid]
            state.converted_to_uid = shipyard.uid
            self._delete_ship(ship, UnitStatus.CONVERTED)

        def convert_board_cell(self, board_cell):
            # TODO: Add logging.
            self._deplete_board_cell(board_cell)

        self._assert_valid_action(player, ship, Ship)

        cost = self.configuration.convert_cost - ship.halite

        if ship.player.halite < cost:
            raise CantConvert("Insufficient halite.")
        if any(ship.pos == shipyard.pos for _, shipyard in player.shipyards):
            raise CantConvert("Shipyard already present.")

        self._state.halite_score[ship.player.index] -= cost
        shipyard = self._create_shipyard(
            pos=ship.pos, player=ship.player, converted_from=ship
        )

        convert_board_cell(self, ship.occupies)
        convert_ship(self, ship, shipyard)

        _LOGGER.info(
            "",
            event_type=Events.CONVERTED,
            ship_uid=ship.uid,
            shipyard_uid=shipyard.uid,
        )

    def _move(self, player, ship, direction):

        self._assert_valid_action(player, ship, Ship)

        state = self._state.unit_states[ship.uid]

        state.halite *= 1 - self._configuration.move_cost
        state.pos = ship.occupies.neighbour(direction).pos

        _LOGGER.info(
            "", event_type=Events.MOVED, ship_uid=ship.uid, direction=direction
        )

        # TODO: Add logging.

    def _mine(self, player, ship):

        self._assert_valid_action(player, ship, Ship)

        state = self._state.unit_states[ship.uid]

        mined_halite = max(ship.occupies.halite * self._configuration.collect_rate, 1)

        state.halite += mined_halite
        self._state.halite_board[ship.pos] -= mined_halite

        _LOGGER.info(
            "", event_type=Events.MINED, ship_uid=ship.uid, halite=mined_halite
        )

    def _deposit(self, player, ship):

        self._assert_valid_action(player, ship, Ship)
        shipyard = ship.occupied_friendly_shipyard
        if shipyard is None:
            raise CantDeposit("Not over a friendly shipyard.")

        deposited_halite = ship.halite

        self._state.halite_score[player.index] += deposited_halite
        self._state.unit_states[ship.uid].halite = 0

        _LOGGER.info(
            "", event_type=Events.DEPOSITED, ship_uid=ship.uid, halite=deposited_halite,
            shipyard_uid=shipyard.uid
        )

    def _create_player(self, index):
        player = Player(index=index, game=self)
        return player

    def _create_unit(self, class_, pos, player, created_at=None, **kwargs):
        create_state_func = (
            UnitState.create_ship if class_ == Ship else UnitState.create_shipyard
        )

        state = create_state_func(
            uid=self._create_uid(),
            pos=pos,
            player_index=player.index,
            created_at=created_at or self._state.step,
            **kwargs,
        )

        unit = class_(game=self, uid=state.uid)

        self._units[unit.uid] = unit
        self._state.unit_states[state.uid] = state
        return unit

    def _create_ship(
        self,
        pos,
        player,
        halite=0,
        status=None,
        created_at=None,
        deleted_at=None,
        converted_to=None,
        spawned_from=None,
    ):
        return self._create_unit(
            class_=Ship,
            pos=pos,
            player=player,
            created_at=created_at,
            halite=halite,
            spawned_from_uid=None if spawned_from is None else spawned_from.uid,
        )

    def _create_shipyard(
        self, pos, player, created_at=None, converted_from=None,
    ):
        return self._create_unit(
            class_=Shipyard,
            pos=pos,
            player=player,
            created_at=created_at,
            converted_from_uid=None if converted_from is None else converted_from.uid,
        )

    def _interpret_actions(self, actions_list):
        """
        Interprets the provided actions.

        Args:
            actions_list (list[dict]): List of actions per player.
        """

        def interpret_action(self, player, unit, action):
            Actions.assert_valid(action)
            if action == "SPAWN":
                self._spawn(player, unit)
            elif action == "CONVERT":
                self._convert(player, unit)
            elif action in ("NORTH", "SOUTH", "EAST", "WEST"):
                self._move(player, unit, direction=action)

        for player, actions in zip(self.players, actions_list):
            for uid, action in actions.items():
                units = dict(player.units)
                if uid not in units:
                    raise InvalidUnitError(uid)
                try:
                    interpret_action(self, player, units[uid], action)
                except ImpossibleAction as error:
                    _LOGGER.error(error)
                except IllegalAction:
                    # TODO: Supposed to make that agent loose.
                    pass

    @property
    def _repr_attrs(self):
        return {
            "configuration": self.configuration,
            "n_players": self.n_players,
            "board": self.board,
        }

    def _collect_halite(self, actions_list):
        for player, actions in zip(self.players, actions_list):
            for uid, ship in player.ships:
                if uid not in actions:
                    if ship.occupied_friendly_shipyard:
                        self._deposit(player, ship)
                    else:
                        self._mine(player, ship)

    def _regenerate_halite(self):
        def regenerate_board_cell(self, board_cell):
            if not any(board_cell.occupied_by) and board_cell.halite:
                new_halite = board_cell.halite * self._configuration.regen_rate
                self._state.halite_board[board_cell.pos] += new_halite
                _LOGGER.debug(
                    "",
                    event_type=Events.REGENERATED,
                    pos=board_cell.pos,
                    halite=new_halite,
                )

        for board_cell in self.board.board_cells:
            regenerate_board_cell(self, board_cell)

    def interpret(self, state, actions):
        with self.load_state(state):
            self.state.step += 1
            clear_contextvars()
            bind_contextvars(step=self.state.step)
            self._interpret_actions(actions)
            self._detect_collision()
            self._collect_halite(actions)
            self._regenerate_halite()
            return self.state

    def _initialize_halite_board(self):
        def _distribute_halite():
            """
            Distribute Halite evenly into quartiles.
            """

            half = math.ceil(size / 2)
            grid = [[0] * half for _ in range(half)]

            # Randomly place a few halite "seeds".
            for i in range(half):
                grid[randint(0, half - 1)][randint(0, half - 1)] = i ** 2

            # Spread the seeds radially.
            radius_grid = copy.deepcopy(grid)
            for r in range(half):
                for c in range(half):
                    value = grid[r][c]
                    if value == 0:
                        continue
                    radius = round((value / half) ** (0.5))
                    for r2 in range(r - radius + 1, r + radius):
                        for c2 in range(c - radius + 1, c + radius):
                            if r2 >= 0 and r2 < half and c2 >= 0 and c2 < half:
                                distance = (abs(r2 - r) ** 2 + abs(c2 - c) ** 2) ** (
                                    0.5
                                )
                                radius_grid[r2][c2] += int(
                                    value / max(1, distance) ** distance
                                )

            return radius_grid

        def _normalize_halite(radius_grid):
            """
            Normalize the available halite against the defined configuration starting halite.
            """
            total = sum([sum(row) for row in radius_grid])
            halite_board = [0] * (size ** 2)
            for r, row in enumerate(radius_grid):
                for c, val in enumerate(row):
                    val = int(val * halite / total / 4)
                    halite_board[size * r + c] = val
                    halite_board[size * r + (size - c - 1)] = val
                    halite_board[size * (size - 1) - (size * r) + c] = val
                    halite_board[size * (size - 1) - (size * r) + (size - c - 1)] = val

            return halite_board

        size = self.configuration.size
        halite = self.configuration.halite

        return _normalize_halite(_distribute_halite())

    def _initialize_ships(self):
        def _distribute_starting_ships():
            starting_positions = [0] * num_agents
            if num_agents == 1:
                starting_positions[0] = size * (size // 2) + size // 2
            elif num_agents == 2:
                starting_positions[0] = size * (size // 2) + size // 4
                starting_positions[1] = size * (size // 2) + math.ceil(3 * size / 4) - 1
            elif num_agents == 4:
                starting_positions[0] = size * (size // 4) + size // 4
                starting_positions[1] = size * (size // 4) + 3 * size // 4
                starting_positions[2] = size * (3 * size // 4) + size // 4
                starting_positions[3] = size * (3 * size // 4) + 3 * size // 4
            return starting_positions

        def _create_starting_ships(self, starting_positions):
            return [
                self._create_ship(pos, player)
                for pos, player in zip(starting_positions, players)
            ]

        size = self.configuration.size
        num_agents = self.n_players
        players = self.players

        return _create_starting_ships(self, _distribute_starting_ships())

    @property
    def initial(self):
        state = State(
            step=0,
            unit_states={},
            halite_score=[self._starting_halite for _ in range(self.n_players)],
            halite_board=self._initialize_halite_board(),
        )
        with self.load_state(state):
            self._initialize_ships()
            return self.state

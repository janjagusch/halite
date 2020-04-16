"""
This module defines the game.
"""

from random import randint
import copy
import operator
import math

from halite.utils import RepresentationMixin, merge_dicts, setup_logger
from halite.interpreter.exceptions import (
    InvalidActionError,
    InvalidUnitError,
    NoStateError,
)
from halite.interpreter.board import Board
from halite.interpreter.player import Player
from halite.interpreter.unit import Ship, Shipyard, Status
from halite.interpreter.state import State


_LOGGER = setup_logger(__name__)


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

    def __init__(self, *, configuration, n_players=4, starting_halite=5000):
        self._configuration = configuration
        self._players = [self._create_player(index) for index in range(n_players)]
        self._board = Board(game=self)
        self._starting_halite = starting_halite
        self._state = None

    @property
    def n_players(self):
        return len(self.players)

    @property
    def starting_halite(self):
        return self._starting_halite

    @property
    def initial(self):
        state = State(
            step=0,
            units={},
            halite_score=[self._starting_halite for _ in range(self.n_players)],
            halite_board=self._initialize_halite_board(),
        )
        self._state = state
        self._initialize_ships()
        self._state = None
        return state

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

    @property
    def step(self):
        return self.state.step

    @property
    def _units(self):
        return self.state.units

    def units(self, player=None, class_=None, status=None):
        return self.state.filter_units(player=player, class_=class_, status=status)

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

        def detect_collision_with_shipyards(self):
            for _, ship in self.ships(status=Status.ACTIVE):
                enemy_shipyard = None
                for unit in ship.occupies.occupied_by:
                    if isinstance(unit, Shipyard) and unit.player != ship.player:
                        enemy_shipyard = unit
                        break
                if enemy_shipyard:
                    _LOGGER.info(
                        f"Collision detected between {ship} and {enemy_shipyard}."
                    )
                    ship.destroy()

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
                    ship.destroy()
                if ships[0].halite == second_largest_halite:
                    ships[0].destroy()
                else:
                    ships[0].damage(second_largest_halite)
                board_cell.destroy()

        detect_collision_with_shipyards(self)
        detect_collision_between_ships(self)

    def spawn(self, player, shipyard):
        assert player == shipyard.player
        ship, cost = shipyard.spawn(self._create_uid())
        self._units[ship.uid] = ship
        self.halite_score[player.index] -= cost
        return ship

    def convert(self, player, ship):
        assert player == ship.player
        shipyard, cost = ship.convert(self._create_uid())
        self._units[shipyard.uid] = shipyard
        self.halite_score[player.index] -= cost
        return shipyard

    def move(self, player, ship, direction):
        assert player == ship.player
        ship.move(direction)

    def mine(self, player, ship):
        assert player == ship.player
        ship.mine()

    def deposit(self, player, ship):
        assert player == ship.player
        halite = ship.deposit()
        self.halite_score[player.index] += halite

    def _create_player(self, index):
        player = Player(index=index, game=self)
        return player

    def _create_unit(self, class_, pos, player, created_at=None, **kwargs):
        unit = class_(
            uid=self._create_uid(),
            pos=pos,
            player=player,
            created_at=created_at or self.step,
            **kwargs,
        )
        self._units[unit.uid] = unit
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
        ship = self._create_unit(
            class_=Ship,
            pos=pos,
            player=player,
            created_at=created_at,
            status=status or Status.ACTIVE,
            halite=halite,
            deleted_at=deleted_at,
            converted_to=converted_to,
            spawned_from=spawned_from,
        )

    def _create_shipyard(
        self,
        pos,
        player,
        created_at=None,
        converted_from=None,
        spawned_ships=None,
        deposit_log=None,
    ):
        return self._create_unit(
            class_=Shipyard,
            pos=pos,
            player=player,
            created_at=created_at,
            converted_from=converted_from,
            spawned_ships=spawned_ships,
            deposit_log=deposit_log,
        )

    def _interpret_actions(self, actions_list):
        """
        Interprets the provided actions.

        Args:
            actions_list (list[dict]): List of actions per player.
        """

        def interpret_action(self, player, unit, action):
            if action == "SPAWN":
                self.spawn(player, unit)
            elif action == "CONVERT":
                self.convert(player, unit)
            elif action in ("NORTH", "SOUTH", "EAST", "WEST"):
                self.move(player, unit, direction=action)
            else:
                raise InvalidActionError(action)

        for player, actions in zip(self.players, actions_list):
            for uid, action in actions.items():
                units = dict(player.units)
                if uid not in units:
                    raise InvalidUnitError(uid)
                interpret_action(self, player, units[uid], action)

    @property
    def _repr_attrs(self):
        return {
            "configuration": self.configuration,
            "n_players": self.n_players,
            "board": self.board,
        }

    def interpret(self, state, actions):
        self._state = copy.deepcopy(state) # this doesnt work because of player references.
        self._interpret_actions(actions)
        self._detect_collision()
        state = self.state
        self._state = None
        return state

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

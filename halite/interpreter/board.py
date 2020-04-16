"""
This module defines what to play the game on: The board and the board's cells.
"""

from kaggle_environments.envs.halite.halite import get_to_pos

from halite.interpreter.exceptions import NoStateError
from halite.interpreter.unit import Status
from halite.utils import RepresentationMixin, setup_logger


_LOGGER = setup_logger(__name__)


class Board(RepresentationMixin):
    """
    A board that constitues of board cells.

    Args:
        board_cells (list): The list of board cells.
        game (halite.interpreter.game.Game): The game.
    """

    def __init__(self, *, game):
        self._game = game
        self._board_cells = [
            BoardCell(pos=pos, board=self)
            for pos in range(game.configuration.size ** 2)
        ]

    @property
    def board_cells(self):
        """
        The board cells.
        """
        return self._board_cells

    @property
    def size(self):
        """
        The size of the board.
        """
        return self.game.configuration.size

    @property
    def game(self):
        """
        The game the board belongs to.
        """
        return self._game

    def __getitem__(self, key):
        return self.board_cells[key]

    def __iter__(self):
        return iter(self.board_cells)

    def regenerate(self):
        """
        Regenerates the halite in all cells on the board (that are not occupied).
        """
        for board_cell in self:
            board_cell.regenerate()

    @property
    def _repr_attrs(self):
        repr_attrs = {"size": self.size}
        if len(self.board_cells) <= 10:
            repr_attrs["board_cells"] = self.board_cells
        return repr_attrs


class BoardCell(RepresentationMixin):
    """
    A board cells that tracks the amount of halite it contains and is aware of its
    neighbours and the units that occupy it.

    Args:
        pos (int): The position.
        board (halite.interpreter.board.BoardMap): The board to this cell
            belongs to.
    """

    def __init__(self, pos, board):
        self._pos = pos
        self._board = board

    @property
    def pos(self):
        """
        The position of the cell.
        """
        return self._pos

    @property
    def halite(self):
        """
        The amount of halite in the cell.
        """
        return self._halite

    @property
    def _game(self):
        return self._board.game

    @property
    def _state(self):
        return self._game.state

    @property
    def halite(self):
        return self._game.state.halite_board[self.pos]

    @property
    def _configuration(self):
        return self._game.configuration

    @property
    def _regen_rate(self):
        return self._configuration.regen_rate

    @property
    def _collect_rate(self):
        return self._configuration.collect_rate

    def neighbour(self, direction):
        """
        Gives you the neighbouring cell in a certain direction.

        Args:
            direction (str): The direction ("NORTH", "EAST", "SOUTH", "WEST").

        Returns:
            halite.interpreter.board.BoardCell: The neighbouring cell.
        """
        return self._board[get_to_pos(self._board.size, self.pos, direction)]

    def __lt__(self, other):
        return self.halite < other.halite

    def __eq__(self, other):
        return self.halite == other.halite

    def __gt__(self, other):
        return self.halite > other.halite

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.halite + other.halite
        return self.halite + other

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            return self.halite + other.halite
        return self.halite + other

    def regenerate(self):
        """
        Regenerates the cell's halite if it is not occupied.
        """
        if not any(self.occupied_by):
            new_halite = self.halite * self._regen_rate
            _LOGGER.debug(f"Cell {self.pos} regenerated {new_halite} halite.")
            self._state.halite_board[self.pos] += new_halite

    def destroy(self):
        """
        Depletes the cell's halite because two ships collided on top of it.
        """
        _LOGGER.info(
            f"Oh no! Cell {self.pos} lost {self.halite} halite in the explosion!"
        )
        self._state.halite_board[self.pos] = 0

    def convert(self):
        """
        Depletes the cell's halite because a shipyard was built on top of it.
        """
        _LOGGER.info(f"Cell {self.pos} lost {self.halite} halite in the construction.")
        self._state.halite_board[self.pos] = 0

    def mine(self):
        """
        Depletes a cell's halite because a ship was mining on top of it.
        """
        mined_halite = self.halite * self._collect_rate
        _LOGGER.debug(f"Cell {self.pos} lost {mined_halite} halite to mining.")
        self._state.halite_board[self.pos] -= mined_halite
        return mined_halite

    @property
    def _repr_attrs(self):
        return {
            "pos": self.pos,
            "halite": self.halite,
        }

    @property
    def occupied_by(self):
        """
        Tells you the units that are currently occupying this cell.

        Returns:
            list: A list of active units occupying this cell.
        """
        for uid, unit in self._game.units(status=Status.ACTIVE):
            if unit.pos is self.pos:
                yield unit

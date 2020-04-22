"""
This module defines what to play the game on: The board and the board's cells.
"""

from kaggle_environments.envs.halite.halite import get_to_pos

from halite.interpreter.exceptions import NoStateError
from halite.interpreter.constants import UnitStatus
from halite.utils import RepresentationMixin


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
        if self.__class__ is other.__class__:
            return self.halite < other.halite
        NotImplemented

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.halite == other.halite
        NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.halite > other.halite
        NotImplemented

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.halite + other.halite
        return self.halite + other

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            return self.halite + other.halite
        return self.halite + other

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
        for uid, unit in self._game.units(status=UnitStatus.ACTIVE):
            if unit.pos is self.pos:
                yield unit

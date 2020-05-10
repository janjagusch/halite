"""
This is a modified version of the default data model supplied by Kaggle/Halite. I'm porting the old bot over
to this because this also outputs the actions.

=== Modifications ===
+ Refactored 
    + get_col_row() and get_to_pos()  methods are now static methods
    + 
+ Added Direction and Action classes to avoid using strings like "NORTH", "SPAWN", "CONVERT" directly



"""

from halite.dtypes import Position, Action, Direction
from dataclasses import dataclass




class Board:
    """
    Takes an observation and structures the data.
    Allows the user to specify actions via the move(), convert(), spawn methods() and handles the
    creation of the return dict that is parsed by the Halite interpreter.
    """
    def __init__(self, obs, config):
        mypid = obs['player']
        
        self.action = {}
        self.players = {} 
        self.config = config
        # self.cells = [BoardCell() for i in range(size) for j in range(size)]
        size = config.size

        for pid, [player_halite, shipyards, ships] in enumerate(obs.players):
            player = Player(board=self, pid=pid, halite=player_halite)

            player.ships = {uid: Ship(
                board=self,
                uid=uid,
                pos=Position(*Board.get_col_row(size, pos), size),
                player=player,
                halite=ship_halite,
            ) for uid, [pos, ship_halite] in ships.items()}

            player.shipyards = {uid: Shipyard(
                board=self,
                uid=uid,
                pos=Position(*Board.get_col_row(size, pos), size),
                player=player,
            ) for uid, pos in shipyards.items()}
            
            self.players[pid] = player

        self.me = self.players[mypid]


        # for uid, pos in shipyards.items():
        #     self.shipyards[pos] = pid
        #     self.shipyards_by_uid[uid] = {"player_index": pid, "uid": uid, "pos": pos}
        
        # for uid, ship in ships.items():
        #     pos, ship_halite = ship
        #     details = {"halite": ship_halite, "player_index": pid, "uid": uid, "pos": pos}
        #     self.ships[pos] = details
        #     self.ships_by_uid[uid] = details
            ## TODO Move to a navigator module instead
            # for direction in [Direction.north, Direction.south, Direction.east, Direction.west]:
            #     self.possible_ships[Board.get_to_pos(size, pos, direction)][uid] = details
    
    @staticmethod
    def get_col_row(size, pos):
        return (pos % size, pos // size)

    # @staticmethod
    # def get_to_pos(size, pos, direction):
    #     col, row = Board.get_col_row(size, pos)
    #     if direction == Direction.north:
    #         return pos - size if pos >= size else size ** 2 - size + col
    #     elif direction == Direction.south:
    #         return col if pos + size >= size ** 2 else pos + size
    #     elif direction == Direction.east:
    #         return pos + 1 if col < size - 1 else row * size
    #     elif direction == Direction.west:
    #         return pos - 1 if col > 0 else (row + 1) * size - 1

    def ship_move(self, ship_uid, direction):
        self.action[ship_uid] = direction

    def ship_convert(self, ship_uid):
        self.action[ship_uid] = Action.convert

    def shipyard_spawn(self, shipyard_uid):
        self.action[shipyard_uid] = Action.spawn

    ## TODO Move to a navigator module instead
    # def __remove_possibles(self, ship_uid):
    #     pos = self.ships_by_uid[ship_uid]["pos"]
    #     for d in [Direction.north, Direction.south, Direction.east, Direction.west]:
    #         to_pos = Board.get_to_pos(self.config.size, pos, d)
    #         del self.possible_ships[to_pos][ship_uid]


@dataclass
class Player:
    board: Board
    pid: int
    ships: dict
    shipyards: dict
    halite: float

    @property
    def units(self):
        return {**self.ships, **self.shipyards}

    def __repr__(self):
        return f"Player({self.pid})"


@dataclass
class Ship:
    board: Board
    uid: str
    pos: Position
    player: Player
    halite: float

    def move(self, direction):
        self.board.ship_move(self.uid, direction)

    def convert(self):
        self.board.ship_convert(self.uid)

    def __repr__(self):
        return f"Ship({self.uid})"


@dataclass
class Shipyard:
    board: Board
    uid: str
    pos: Position
    player: Player

    def spawn(self):
        self.board.shipyard_spawn(self.uid)

    def __repr__(self):
        return f"Shipyard({self.uid})"


@dataclass
class BoardCell:
    board: Board
    pos: Position
    units: dict = {}

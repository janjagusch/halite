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
        ## TODO populate for when the BoardCell class is finished
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
    
    @staticmethod
    def get_col_row(size, pos):
        return (pos % size, pos // size)

    def ship_move(self, ship_uid, direction):
        self.action[ship_uid] = direction

    def ship_convert(self, ship_uid):
        self.action[ship_uid] = Action.convert

    def shipyard_spawn(self, shipyard_uid):
        self.action[shipyard_uid] = Action.spawn


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


# TODO: Complete this class
@dataclass
class BoardCell:
    board: Board
    pos: Position
    halite: float
    units: dict = {}
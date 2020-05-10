# import logging
# from utils import get_turns_left_rel, get_halite_left_rel

import halite.constants as consts


class Spawner():
    def __init__(self, config):
        self.config = config

    def __call__(self, board, strategy):
        return self.spawn(board, strategy)

    def spawn(self, board, strategy):
        raise NotImplementedError


class GreedySpawner(Spawner):

    MAX_SHIPS: int = 15

    def spawn(self, board, strategy):
        for shipyard in board.shipyards:
            if board.step < 350 and len(board.ships) < self.MAX_SHIPS and board.me.halite > consts.SPAWN_COST:
                shipyard.spawn()

import copy
import json
import math
import random
from os import path
from halite.agents.agent import Agent
from random import choice, randint, shuffle
from .board import Board

class RandomAgent(Agent):
    """
    Bot that doesn't know what to do
    (this is the default impl included with the kaggle env)
    """

    def __init__(self, config, agentid=0, game_log=None):
        self.agentid = agentid
        if game_log is None:
            pass
        self.game_log = game_log
        self.config = config

    def act(self, obs):
        size = self.config.size
        halite = obs.halite
        board = Board(obs, self.config)
        player_halite, shipyards, ships = obs.players[obs.player]  

        # Move, Convert, or have ships collect halite.
        ships_items = list(ships.items())
        shuffle(ships_items) # shuffle so ship1 doesn't always have first moving dibs.
        for uid, ship in ships_items:
            pos, ship_halite = ship
            # Collect Halite (50% probability when cell halite > ship_halite).
            if board.shipyards[pos] == -1 and halite[pos] > ship_halite and randint(0,1) == 1:
                continue
            # Convert to Shipyard (50% probability when no shipyards, 5% otherwise).
            if board.shipyards[pos] == -1 and player_halite > self.config.convertCost and randint(0, 20 if len(shipyards) else 1) == 1:
                board.convert(uid)
                continue
            # Move Ship (random between all available directions).
            move_choices = [None]
            for direction in ["NORTH", "EAST", "SOUTH", "WEST"]:
                to_pos = Board.get_to_pos(size, pos, direction)
                # Enemy shipyard present.
                if board.shipyards[to_pos] != obs.player and board.shipyards[to_pos] != -1:
                    continue
                # Larger ship most likely staying in place.
                if board.ships[to_pos] is not None and board.ships[to_pos]["halite"] >= ship_halite:
                    continue
                # Weigh the direction based on number of possible larger ships that could be present.
                weight = 6
                if board.ships[to_pos] is not None and board.ships[to_pos]["player_index"] == obs.player:
                    weight -= 1
                for s in board.possible_ships[to_pos].values():
                    if s["halite"] > ship_halite:
                        weight -= 1
                move_choices += [direction] * weight
            move = choice(move_choices)
            if move is not None:
                board.move(uid, move)
                
        # Spawn ships (30% probability when possible, or 100% if no ships).
        for uid, pos in shipyards.items():
            if board.ships[pos] is None and player_halite >= self.config.spawnCost and (randint(0,2) == 2 or len(ships_items) == 0):
                board.spawn(uid)
        
        return board.action

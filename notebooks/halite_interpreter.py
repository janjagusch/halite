# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python (halite)
#     language: python
#     name: connect-x
# ---

# # Jan's Halite Interpreter: A Walkthrough

import sys

sys.path.append("..")

from kaggle_environments import make

from halite.interpreter.game import Game
from halite.interpreter.configuration import Configuration
from halite.interpreter.board_map import BoardMap
from halite.interpreter.player import Player
from halite.interpreter.unit import Shipyard, Ship

env = make("halite")
_ = env.reset()
state = env.state

configuration = Configuration(env.configuration)
configuration

game = Game(configuration, players=[], board_map=None, step=1)
game

# ## Board Map

# +
board_map = BoardMap(game=game, board_cells=None)
game.board_map = board_map
board_map.board_cells_from_halite(env.state[0].observation.halite)

board_map
# -

board_map[0]

min(board_map)

sum(board_map)

board_map.regenerate()

# ## Player & Units

from halite.interpreter.unit import _create_uid

# +
player_0 = Player(index=0, halite=10000, shipyards={}, ships={}, game=game)
game.players.append(player_0)

player_0
# -

# ### Shipyard

# +
shipyard_0_0 = Shipyard(
    uid=_create_uid(game.step),
    pos=100,
    player=player_0,
    created_at=game.step,
    converted_from=None,
)
player_0.shipyards[shipyard_0_0.uid] = shipyard_0_0

shipyard_0_0
# -

ship_0_0 = shipyard_0_0.spawn()

player_0.halite = 0

shipyard_0_0.spawn()

player_0.halite = 10000

# ### Ship

ship_0_0.spawned_from

ship_0_0.occupies

ship_0_0.move("NORTH")

ship_0_0.move("SOUTH")

ship_0_0.mine()

ship_0_0.move("SOUTH")

ship_0_0.convert()

player_0

ship_0_0.move("NORTH")

ship_0_1 = shipyard_0_0.spawn()

ship_0_1._halite = 1000

ship_0_1.deposit()

ship_0_1.destroy()

ship_0_1.convert()

# ## Collision Detection

player_1 = Player(index=1, halite=10000, shipyards={}, ships={}, game=game)
game.players.append(player_1)
player_1

shipyard_1_0 = Shipyard(
    uid=_create_uid(game.step),
    pos=200,
    player=player_1,
    created_at=game.step,
    converted_from=None,
)
player_1.shipyards[shipyard_1_0.uid] = shipyard_1_0

ship_0_2 = shipyard_0_0.spawn()
ship_0_2._pos = shipyard_1_0.pos

game.detect_collision()

shipyard_0_0.spawn()
shipyard_0_0.spawn()
ship_0_3 = shipyard_0_0.spawn()
ship_0_3._halite = 1000

game.detect_collision()

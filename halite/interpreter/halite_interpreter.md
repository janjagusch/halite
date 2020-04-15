# The Halite Interpreter

## Input

* state
* env

## Process

* if env.done:
    * initialize the board.
* apply actions:
    * spawn
    * convert
    * move
* detect collision
    * ship vs shipyard
    * ship vs ship
* remove invalid players
* collect halite
* regenerate halite
* check if done
* update reward

## Output

* state

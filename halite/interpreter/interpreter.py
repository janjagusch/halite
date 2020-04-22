from typing import List

from kaggle_environments.core import Environment
from kaggle_environments.utils import Struct

from .constants import PlayerStatus
from .configuration import Configuration
from .player import Player
from .game import Game
from .state import State


def _reward(player: Player) -> int:
    if player.status in (PlayerStatus.ACTIVE, PlayerStatus.DONE):
        return player.halite
    return 0


def _done(game: Game) -> bool:
    active_players = list(
        filter(lambda player: player.status == PlayerStatus.ACTIVE, game.players)
    )
    return len(active_players) <= 1 and len(game.players) > 1


def _player_status(player: Player, done: bool) -> str:
    if done and player.status == PlayerStatus.ACTIVE:
        return PlayerStatus.DONE
    return player.status


def _to_player_state(
    state: State, player_index: int, reward: int, status: str
) -> Struct:
    return Struct(
        action={},
        reward=reward,
        info={},
        observation=state.to_observation(player_index),
        status=status,
    )


def _to_state(game: Game, state: State) -> List[Struct]:

    with game.load_state(state):
        done = _done(game)
        rewards = [_reward(player) for player in game.players]
        statuses = [_player_status(player, done) for player in game.players]

    return [
        _to_player_state(state, player_index, reward, status)
        for player_index, (reward, status) in enumerate(zip(rewards, statuses))
    ]


def interpret(state: Struct, env: Environment) -> Struct:

    configuration = Configuration.from_kaggle_env_configuration(env.configuration)
    game = Game(configuration=configuration, n_players=len(state))

    if env.done:
        state = game.initial
    else:
        actions = [player_state.action or {} for player_state in state]
        observation = state[0].observation
        state = State.from_observation(observation)
        state = game.interpret(state, actions)

    return _to_state(game, state)

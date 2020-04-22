from typing import Union, Dict, List
from dataclasses import dataclass, field

from kaggle_environments.utils import Struct


@dataclass
class Unit:

    uid: str = field()
    pos: str = field()
        
@dataclass
class Ship(Unit):
    
    halite: Union[float, None] = field()
        
@dataclass
class Shipyard(Unit):
    pass
    
@dataclass
class Player:
    
    halite: float = field()
    shipyards: Dict[str, Shipyard] = field()
    ships: Dict[str, Ship]
        
    @classmethod
    def from_kaggle_env_observation(cls, player: List):
        return cls(
            halite=player[0],
            shipyards={uid: Shipyard(uid, pos) for uid, pos in player[1].items()},
            ships={uid: Ship(uid, pos, halite) for uid, (pos, halite) in player[2].items()},
        )
    
    def to_kaggle_env_observation(self) -> List:
        return [
            self.halite,
            {uid: shipyard.pos for uid, shipyard in self.shipyards.items()},
            {uid: [ship.pos, ship.halite] for uid, ship in self.ships.items()}
        ]
        
@dataclass
class Observation:
    
    step: int = field()
    halite: List[float] = field()
    players: List[Player] = field()
        
    @classmethod
    def from_kaggle_env_observation(cls, observation: Struct):
        return cls(
            step=observation.step,
            halite=observation.halite,
            players=[Player.from_kaggle_env_observation(player) for player in observation.players]
        )
    
    def to_kaggle_env_observation(self, player) -> Struct:
        return Struct(
            player=player,
            step=self.step,
            halite=self.halite,
            players=[player.to_kaggle_env_observation() for player in self.players]
        )

@dataclass
class Agent:

    action: Dict[str, str] = field()
    reward: float = field()
    info: Dict[str, str] = field()
    status: str = field()

    @classmethod
    def from_kaggle_env_agent(cls, agent: Struct):
        return cls(
            action=agent.action,
            reward=agent.reward,
            info=agent.info,
            status=agent.status
        )

    def to_kaggle_env_agent(self, observation):
        return Struct(
            action=self.action,
            reward=self.reward,
            info=self.info,
            status=self.status,
            observation=observation
        )


@dataclass
class State:

    agents: List[Agent] = field()
    observation: Observation = field()

    @classmethod
    def from_kaggle_env_state(cls, state: List[Struct]):
        return cls(
            agents = [Agent.from_kaggle_env_agent(agent) for agent in state],
            observation = Observation.from_kaggle_env_observation(state[0].observation)
        )

    def to_kaggle_env_state(self) -> List[Struct]:
        return [
            agent.to_kaggle_env_agent(self.observation.to_kaggle_env_observation(index)) for index, agent in enumerate(self.agents)
        ]

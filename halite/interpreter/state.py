"""
This module defines the game.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict

from kaggle_environments.utils import Struct

from halite.interpreter.constants import UnitStatus, UnitType
from halite.utils import DataClassYamlMixin


@dataclass(order=True, unsafe_hash=True)
class UnitState(DataClassYamlMixin):
    # Basic unit attributes.
    uid: str = field()
    unit_type: str = field(compare=False, hash=False)
    pos: Union[int, None] = field(compare=False, hash=False)
    player_index: int = field(compare=False, hash=False)
    created_at: int = field(hash=False, compare=False)
    deleted_at: Union[int, None] = field(
        hash=False, compare=False, init=False, default=None
    )
    unit_status: str = field(default=UnitStatus.ACTIVE, compare=False)
    # Ship attributes.
    converted_to_uid: Union[str, None] = field(
        compare=False, hash=False, init=False, default=None
    )
    spawned_from_uid: Union[str, None] = field(compare=False, hash=False, default=None)
    halite: Union[int, None] = field(compare=False, hash=False, default=None)
    # Shipyard attributes.
    spawned_ship_uids: Union[List[str], None] = field(
        default=None, compare=False, hash=False
    )
    deposit_log: Union[List[dict], None] = field(
        default=None, compare=False, hash=False
    )
    converted_from_uid: Union[str, None] = field(
        compare=False, hash=False, default=None
    )

    @classmethod
    def create_ship(
        cls, *, uid, pos, player_index, created_at, spawned_from_uid, halite=0
    ):
        return cls(
            uid=uid,
            unit_type=UnitType.SHIP,
            pos=pos,
            player_index=player_index,
            created_at=created_at,
            spawned_from_uid=spawned_from_uid,
            halite=halite,
        )

    @classmethod
    def create_shipyard(cls, *, uid, pos, player_index, created_at, converted_from_uid):
        return cls(
            uid=uid,
            unit_type=UnitType.SHIPYARD,
            pos=pos,
            player_index=player_index,
            created_at=created_at,
            converted_from_uid=converted_from_uid,
            spawned_ship_uids=[],
            deposit_log=[],
        )

    @classmethod
    def from_observation(cls, uid, values, unit_type, player_index):
        UnitType.assert_valid(unit_type)
        if unit_type == UnitType.SHIP:
            pos, halite = values
            return cls.create_ship(
                uid=uid,
                pos=pos,
                player_index=player_index,
                created_at=None,
                spawned_from_uid=None,
                halite=halite,
            )
        if unit_type == UnitType.SHIPYARD:
            return cls.create_shipyard(
                uid=uid,
                pos=values,
                player_index=player_index,
                created_at=None,
                converted_from_uid=None,
            )

    def to_observation(self):
        UnitType.assert_valid(self.unit_type)
        if self.unit_type == UnitType.SHIP:
            return [self.pos, self.halite]
        return self.pos


@dataclass(order=True, unsafe_hash=True)
class State(DataClassYamlMixin):
    step: int = field()
    unit_states: Dict[str, UnitState] = field(
        compare=False, hash=False, default_factory=list
    )
    halite_score: List[int] = field(compare=False, hash=False, default_factory=list)
    halite_board: List[int] = field(compare=False, hash=False, default_factory=list)

    def create_uid(self):
        return f"{self.step}-{len(self.unit_states)}"

    @classmethod
    def from_observation(cls, observation):

        unit_states = {}
        for player_index, player in enumerate(observation.players):
            halite, shipyards, ships = player
            for uid, pos in shipyards.items():
                unit_states[uid] = UnitState.from_observation(
                    uid, pos, UnitType.SHIPYARD, player_index
                )
            for uid, values in ships.items():
                unit_states[uid] = UnitState.from_observation(
                    uid, values, UnitType.SHIP, player_index
                )

        return cls(
            step=observation.step,
            halite_board=observation.halite,
            halite_score=[player[0] for player in observation.players],
            unit_states=unit_states,
        )

    def to_observation(self, player_index):
        """Returns a struct."""

        def player_to_observation(self, player_index):
            shipyards = {
                uid: unit_state.to_observation()
                for uid, unit_state in self.unit_states.items()
                if unit_state.player_index == player_index
                and unit_state.unit_status == UnitStatus.ACTIVE
                and unit_state.unit_type == UnitType.SHIPYARD
            }

            ships = {
                uid: unit_state.to_observation()
                for uid, unit_state in self.unit_states.items()
                if unit_state.player_index == player_index
                and unit_state.unit_status == UnitStatus.ACTIVE
                and unit_state.unit_type == UnitType.SHIP
            }

            return [self.halite_score[player_index], shipyards, ships]

        return Struct(
            player=player_index,
            step=self.step,
            halite=self.halite_board,
            players=[
                player_to_observation(self, pl_ind)
                for pl_ind in range(len(self.halite_score))
            ],
        )

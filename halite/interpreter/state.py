"""
This module defines the game.
"""

from dataclasses import dataclass, field
from itertools import count
from typing import List, Optional, Union, Dict

from halite.interpreter.constants import UnitStatus, UnitType
from halite.utils.representation_mixin import DataClassYamlMixin


_UID = count()


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


@dataclass(order=True, unsafe_hash=True)
class State(DataClassYamlMixin):
    step: int = field()
    unit_states: Dict[str, UnitState] = field(
        compare=False, hash=False, default_factory=list
    )
    halite_score: List[int] = field(compare=False, hash=False, default_factory=list)
    halite_board: List[int] = field(compare=False, hash=False, default_factory=list)

    def create_uid(self):
        return f"{self.step}-{next(_UID)}"

"""
This module defines the game configuration.
"""

from dataclasses import dataclass, field

from kaggle_environments.utils import Struct

from halite.utils import DataClassYamlMixin, camel_to_snake, snake_to_camel


@dataclass
class Configuration(DataClassYamlMixin):
    """
    The Kaggle environment configuration but snake_cased and YAML serializable.
    """

    episode_steps: int = field()
    agent_exec: str = field()
    agent_timeout: int = field()
    act_timeout: int = field()
    run_timeout: int = field()
    halite: int = field()
    size: int = field()
    spawn_cost: int = field()
    convert_cost: int = field()
    move_cost: float = field()
    collect_rate: float = field()
    regen_rate: float = field()

    @classmethod
    def from_kaggle_env_configuration(
        cls, kaggle_configuration: Struct
    ):
        """
        
        """
        return cls(
            **{
                camel_to_snake(key): value
                for key, value in kaggle_configuration.items()
            }
        )

    def to_kaggle_env_configuration(self) -> Struct:
        return Struct(
            **{snake_to_camel(key): value for key, value in vars(self).items()}
        )

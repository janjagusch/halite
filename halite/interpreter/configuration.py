"""
This module defines the game configuration.
"""

from halite.utils import RepresentationMixin


class Configuration(RepresentationMixin):
    """
    The game configuration.

    Args:
        config (dict): The original configuration.
    """

    def __init__(self, config):
        self._config = config or {}

    # pylint: disable=missing-function-docstring

    @property
    def episode_steps(self):
        return self._config.get("episodeSteps")

    @property
    def agent_exec(self):
        return self._config.get("agentExec")

    @property
    def agent_timeout(self):
        return self._config.get("agentTimeout")

    @property
    def act_timeout(self):
        return self._config.get("actTimeout")

    @property
    def run_timeout(self):
        return self._config.get("runTimeout")

    @property
    def halite(self):
        return self._config.get("halite")

    @property
    def size(self):
        return self._config.get("size")

    @property
    def spawn_cost(self):
        return self._config.get("spawnCost")

    @property
    def convert_cost(self):
        return self._config.get("convertCost")

    @property
    def move_cost(self):
        return self._config.get("moveCost")

    @property
    def collect_rate(self):
        return self._config.get("collectRate")

    @property
    def regen_rate(self):
        return self._config.get("regenRate")

    @property
    def _repr_attrs(self):
        return {
            name: getattr(self, name)
            for name, attr in vars(self.__class__).items()
            if isinstance(attr, property) and not name.startswith("_")
        }

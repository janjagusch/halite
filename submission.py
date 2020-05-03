"""
The main entrypoint for this project.
"""
from kaggle_environments.envs.halite.halite import random_agent


def act(observation, configuration):
    """
    Acts upon an observation and a configuration.

    Args:
        observation (kaggle_environments.utils.Struct): The observation.
        configuration (kaggle_environments.utils.Struct): The configuration.

    Returns:
        dict[str, str]: The actions.
    """
    return random_agent(observation, configuration)

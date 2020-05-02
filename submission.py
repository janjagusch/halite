from kaggle_environments.envs.halite.halite import random_agent


def act(observation, configuration):
    return random_agent(observation, configuration)

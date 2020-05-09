import importlib

"""
In preparation for Kaggles dumb rules about single file submissions, this is a very ugly
attempt at making a library of bots that can be initialised using something like 
Agent("myAgent") without having to import them all or creating a registry of bots. This way
stickytape can be used to generate standalone files that only contain the code for a single bot.
"""

def make_agent(agent_name, *args, **kwargs):
    """
    Agent factory, takes in the name of the agent you want to import (the name of the submodule in
    halite.agents), and instantiates it with the arguments you give. The act() method of the agent 
    is then wrapped in a function. This is necessary, as Kaggle requires a function as input.
    """
    agent = importlib.import_module(f"halite.agents.{agent_name}").Agent(*args, **kwargs)
    return lambda obs: agent.act(obs)


class Agent:
    """
    Abstract class that defines outlines of any bot.
    Might get more complex in the future.
    """

    def __init__(self, config, agentid=0, game_log=None):
        self.agentid = agentid
        if game_log is None:
            pass
        self.game_log = game_log
        self.config = config

    def __call__(self, observation, config=None):
        return self.act(observation)

    def act(self, observation, config=None):
        raise NotImplementedError

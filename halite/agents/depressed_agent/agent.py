import random
from halite.agents.agent import Agent

class DepressedAgent(Agent):
    """
    Bot that doesn't feel like doing anything
    """

    def act(self, observation, config=None):
        return []

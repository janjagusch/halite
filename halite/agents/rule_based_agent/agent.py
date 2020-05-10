import timeit
from halite.agents.agent import Agent
from .board import Board
from .spawn import ShipSpawner
from .navigate import DumbNavigator
from .strategy import Strategy




class RuleBasedAgent(Agent):
    """
    Rule based bot that should hopefully be better than the default bot.
    """

    def __init__(self, config, agentid=0, game_log=None, ship_spawner=ShipSpawner, strategy=Strategy):
        super().__init__(config, agentid=0, game_log=None)
        self.strategy = Strategy(config)
        self.navigate = DumbNavigator(config)
        self.spawner = ShipSpawner(config)


    def act(self, observation, config=None):
        if config is None:
            config = self.config

        # Create the data model
        board = Board(observation, config)

        # Create the strategy (a set of objectives)
        strategy = self.strategy(board)
        
        # Navigate the ships towards their objectives
        self.navigate(board, strategy)

        # Decide whether to spend halite on new ships
        self.spawner(board, strategy)

        return board.action

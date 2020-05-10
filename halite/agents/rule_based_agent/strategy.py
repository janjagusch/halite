# import logging
# import pickle
# import timeit
# import random
import numpy as np
# import utils
from dataclasses import dataclass
from halite.dtypes import Position, Direction
from halite.constants import SPAWN_COST
# from hlt.positionals import Position
# import hlt.constants as constants
# from .navigate import AStarNavigator
# from .search import get_neighbours, make_mining_dict


class Strategy:
    def __init__(self, config):
        self.config = config
        self.objectives = {}

    def __call__(self, board):
        return self.strategize(board)

    def strategize(self, board):
        """
        Assign objectives to each unit.
        """
        raise NotImplementedError

    def __getitem__(self, unit):
        """
        Return the Objective associated with the given uid
        """
        uid = unit if type(unit) is str else unit.uid
        return self.objectives[uid]


class GreedyStrategy(Strategy):
    def strategize(self, board):
        """
        Assign objectives to each unit.
        """
        
        self._complete_objectives(board)
        self._find_hotspots(board)
        self._assign_objectives(board)

        return self

    def _complete_objectives(self, board):
        # Remove completed Objectives
            # If ship completes MiningObjective, assign DepositObjective to closest shipyard
            # Else, ship is free
        for uid, objective in self.objectives.items():
            unit = board.me.units[uid]
            if objective.complete(board, unit):
                next_objective = objective.next(board, unit)
                del self.objectives[unit]
                if next_objective is not None:
                    self.objectives[unit] = next_objective
                

    def _find_hotspots(self, board):
        # Identify attractive mining spots
        pass

    def _assign_objectives(self, board, available_objectives):
        # Assign mining locations to available ships
            # For each spot, find the closest ship and assign
            # Update the list of available ships
        
        available_ships = {
            uid: ship 
            for uid, ship in board.me.ship.items() 
            if uid not in self.objectives
        }

        for objective in available_objectives:
            closest = min(
                available_ships,keys(), 
                key=lambda uid: objective.pos.distance(board.me.ships[uid].pos)
            )
            self.objectives[closest] = objective
            del available_ships[closest]






@dataclass
class Objective:
    pos: Position

    def complete(self, board, unit):
        raise NotImplementedError

    def next(self, board, unit):
        return None


class MineObjective(Objective):
    """

    """
    def complete(self, board, unit):
        game_map = game.game_map
        rel_penalty = np.sqrt(utils.get_halite_left_rel(game))
       
        minimum_halite_cell = 200. * rel_penalty
        minimum_halite_ship = 900. * rel_penalty
        if game_map[self.[pos]].halite_amount < minimum_halite_cell or self.ship_log.halite_amount > minimum_halite_ship:
            return True
        else:
            return False

    def next(self, board, unit):
        # Find closest shipyard
        closest = min(
            board.me.shipyards,keys(), 
            key=lambda uid: unit.pos.distance(board.me.shipyards[uid].pos)
        )
        return DepositObjective(board.me.shipyards[closest].pos)

class DepositObjective(Objective):
    """

    """
    def complete(self, board, unit):
        if unit.pos == self.pos:
            return True
        else:
            return False


class ConvertObjective(Objective):
    """ 

    """
    def complete(self, board, unit):
        """
        Once assinged, the unit should be a shipyard the next turn
        """
        return True


class EndGameObjective(Objective):
    """ 

    """
    def complete(self, board, unit):
        return False


class DefendObjective(Objective):
    """ 

    """
    def complete(self, board, unit):
        if self.ship_position == self.position:
            return True
        else:
            return False


class Objective_old:

    def __init__(self, ship_log, position, turn_created, turn_terminated=None, was_fullfilled=None, navigator=None):
        self.ship_log = ship_log
        self.position = position
        if navigator is None:
            navigator = AStarNavigator(step_penalty=50)
        self.navigator = navigator
        self.turn_created = turn_created
        self.turn_terminated = turn_terminated
        self.was_fullfilled = was_fullfilled


    def __repr__(self):
        return "{}(position={}, navigator={})".format(self.__class__.__name__, self.position, self.navigator)


    def execute(self, game, mining_log, occupied_log, enemy_position_dict, timeout):
        game_map = game.game_map
        start_pos = self.ship_log.position
        goal_pos = self.position
        halite_amount = self.ship_log.halite_amount
        t = game.turn_number

        return self.navigator.navigate(game_map=game_map, start_pos=start_pos, goal_pos=goal_pos, halite_amount=halite_amount, mining_log=mining_log, occupied_log=occupied_log, enemy_position_dict=enemy_position_dict, t=t, timeout=timeout)


    def fullfilled(self, game):
        pass


    def failed(self, game):
        buffer = 50
        if game.turn_number > self.turn_created + buffer:
            return True
        else:
            return False





class Strategy_old:

    def __init__(self, objectives=None, objectives_log=None, analysis=None):
        if objectives is None:
            objectives = set()
        self.objectives = objectives
        if objectives_log is None:
            objectives_log = set()
        self.objectives_log = objectives_log
        if analysis is None:
            analysis = dict()
        self.analysis = analysis


    def get_step_penalty(self, game):
        # Let's start with a simple heuristic and add intelligence whenever necessary.
        rel_penalty = np.sqrt(utils.get_halite_left_rel(game))
        return 50. * rel_penalty


    def analyse_game(self, game, player=None):

        step_penalty = self.get_step_penalty(game)

        n = game.turn_number
        if n not in self.analysis.keys():
            game_map = game.game_map
            if player is None:
                player = game.me

            # Update the maps
            np_map = utils.get_np_map(game_map)
            halite_map = utils.get_halite_map(np_map)
            halite_density = utils.approximate_density(halite_map)
            # ship_density = utils.approximate_density(self.halite_map)
            nearest_dropoff_map = np.vectorize(
                lambda cell: utils.get_closest_player_dropoff_to_cell(game, player, cell)[1]
            )(np_map)

            # Dropoff points and shipyards are given a very low score
            nearest_dropoff_map[nearest_dropoff_map == 0] = 100
            weighted_halite_map = halite_map - (nearest_dropoff_map * step_penalty/2)

            self.analysis[n] = dict(
                halite_map=halite_map,
                halite_density=halite_density,
                weighted_halite_map=weighted_halite_map
            )

        return self.analysis[n]


    def next_defend_objective(self, game, ship):
        # TODO:
        return False


    def next_deposit_objective(self, game, ship):
        rel_penalty = np.sqrt(utils.get_halite_left_rel(game))
        if ship.halite_amount >= 900 * rel_penalty:
            return True
        else:
            return False


    def next_end_game_objective(self, game, ship):
        if type(ship.objective) is EndGameObjective:
            return False
        # Let's start with a simple condition and see how well it performs.
        _, distance = utils.get_closest_dropoff_to_ship(game, ship)
        if distance + 10 >= utils.get_turns_left(game):
            return True
        else:
            return False


    def next_mining_objective(self, game, ship):
        rel_penalty = np.sqrt(utils.get_halite_left_rel(game))
        if ship.halite_amount < 900 * rel_penalty:
            return True
        else:
            return False


    def next_conversion_objective(self, game, ship):
        # TODO:
        return False


    def make_mining_objective(self, game, ship):
        # game_map = game.game_map
        # turn_created = game.turn_number
        # np_map = utils.get_np_map(game_map)
        # ship_position = ship.position
        # halite_amount = ship.halite_amount
        # shipyard_position = game.me.shipyard.position
        #
        # distance_to_ship = np.vectorize(lambda x: game_map.calculate_distance(ship_position, x.position))(np_map)
        # distance_to_shipyard = np.vectorize(lambda x: game_map.calculate_distance(shipyard_position, x.position))(np_map)
        # distance = distance_to_ship + distance_to_shipyard
        #
        # halite = np.vectorize(lambda x: min(constants.MAX_HALITE, x.halite_amount))(np_map)
        #
        # score = halite - step_penalty * distance
        # score = score.reshape(-1, )
        #
        # logging.info(score)
        #
        # position = np_map.reshape(-1, )[np.argmax(score)].position
        #
        # logging.info(position)
        #
        # objective = MineObjective(ship, position, turn_created)

        # return objective

        game_map = game.game_map
        step_penalty = self.get_step_penalty(game)
        analysis = self.analyse_game(game)

        # Create priority map.
        priority_map = analysis['weighted_halite_map'] - step_penalty / 2 * utils.get_distance_map(game, ship.position_log[-1])

        # with open("priority_map.p", "wb") as f:
        #     pickle.dump(priority_map, f)
        # with open("game_map.p", "wb") as f:
        #     pickle.dump(game.game_map, f)

        np_map = utils.get_np_map(game_map)
        position_map = np.vectorize(lambda x: x.position)(np_map)
        position_map = position_map.reshape(-1, )
        position_map = position_map[priority_map.reshape(-1, ).argsort()]
        position_map = position_map.reshape(-1, )[priority_map.reshape(-1, ).argsort()]

        # logging.info("position_map: {}".format(position_map.shape))

        condition = condition = np.isin(position_map, [o.position for o in self.objectives], invert=True)
        position_map = position_map[condition]

        # logging.info("position_map: {}".format(position_map.shape))

        position = position_map[-1]

        # logging.info("position: {}".format(position))

        # Random choice in case there are several good choices
        # target_y, target_x = random.choice(np.transpose(np.where(priority_map == priority_map.max())))
        # position = Position(int(target_x), int(target_y))

        turn_created = game.turn_number
        navigator = AStarNavigator(step_penalty=50, end_game=False)

        objective = MineObjective(ship_log=ship, position=position, turn_created=turn_created, navigator=navigator)
        return objective


    def make_defend_objective(self, game, ship):
        # TODO:
        pass


    def make_end_game_objective(self, game, ship):
        position = game.me.shipyard.position
        turn_created = game.turn_number
        navigator = AStarNavigator(step_penalty=100, end_game=True)

        objective = EndGameObjective(ship_log=ship, position=position, turn_created=turn_created, navigator=navigator)
        return objective


    def make_deposit_objective(self, game, ship):
        position = game.me.shipyard.position
        turn_created = game.turn_number
        navigator = AStarNavigator(step_penalty=50, end_game=False)

        objective = DepositObjective(ship_log=ship, position=position, turn_created=turn_created, navigator=navigator)
        return objective


    def make_conversion_objective(self, game, ship):
        # TODO:
        pass


    def make_objective(self, ship_log, game, end_game=False):
        # If next defend objective, make defend objective.
        if self.next_defend_objective(game, ship_log):
            objective = self.make_defend_objective(game, ship_log)

        # If next end game objective, make end game objective.
        elif end_game:
            objective = self.make_end_game_objective(game, ship_log)

        # If next deposit objective, make deposit objective.
        elif self.next_deposit_objective(game, ship_log):
            objective = self.make_deposit_objective(game, ship_log)

        # If next conversion (to dropoff) objective, make conversion objective:
        elif self.next_conversion_objective(game, ship_log):
            objective = self.make_conversion_objective(game, ship_log)

        # Else, make mining objective.
        else:
            objective = self.make_mining_objective(game, ship_log)

        logging.info("created objective {} for ship {}".format(objective, ship_log))

        return objective


    def update_objectives(self, game, game_log, player=None):
        # Assign initial variables.
        if player is None:
            player = game.me
        turn_terminated = game.turn_number

        # Iterate through player's ships.
        for ship in player.get_ships():
            ship_log = game_log.player_logs[player.id].ship_logs[ship.id]

            # If ship has just been spawned, create objective.
            if ship_log.objective is None:
                objective = self.make_objective(ship_log, game)
                ship_log.objective = objective
                self.objectives.add(ship_log.objective)

            # If is end game, create deposit objective.
            elif self.next_end_game_objective(game, ship_log):
                ship_log.objective.turn_terminated = turn_terminated
                ship_log.objective.was_fullfilled = False
                self.objectives_log.add(ship_log.objective)
                self.objectives.remove(ship_log.objective)
                logging.info("objective {} terminated for end game at ship {}.".format(ship_log.objective, ship_log))
                objective = self.make_objective(ship_log, game, end_game=True)
                ship_log.objective = objective
                self.objectives.add(ship_log.objective)

            # If objective fullfilled, assign new objective.
            elif ship_log.objective.fullfilled(game):
                ship_log.objective.turn_terminated = turn_terminated
                ship_log.objective.was_fullfilled = True
                self.objectives_log.add(ship_log.objective)
                self.objectives.remove(ship_log.objective)
                logging.info("objective {} fullfilled at ship {}.".format(ship_log.objective, ship_log))
                objective = self.make_objective(ship_log, game)
                ship_log.objective = objective
                self.objectives.add(ship_log.objective)

            # If objective failed, assign new objective.
            elif ship_log.objective.failed(game):
                ship_log.objective.turn_terminated = turn_terminated
                ship_log.objective.was_fullfilled = False
                self.objectives_log.add(ship_log.objective)
                self.objectives.remove(ship_log.objective)
                logging.info("objective {} failed at ship {}.".format(ship_log.objective, ship_log))
                objective = self.make_objective(ship_log, game)
                ship_log.objective = objective
                self.objectives.add(ship_log.objective)

        # Iterate through objectives and see whether they are still relevant.
        for objective in self.objectives.copy():
            if objective.ship_log.id not in [ship.id for ship in player.get_ships()]:
                objective.turn_terminated = turn_terminated
                objective.was_fullfilled = False
                self.objectives_log.add(objective)
                self.objectives.remove(objective)


    def execute(self, game, game_log, player, max_time):
        """
        Execute Strategy of ships. Stops after max time has passed.
        """
        # Initialise important variables.
        start_time = timeit.default_timer()
        command_queue = []
        game_map = game.game_map
        t = game.turn_number
        mining_log = {}
        occupied_log = {}

        # If player will spwan ship, log shipyard position as occupied.
        if game_log.player_logs[player.id].spawn:
            occupied_log[t + 1] = [player.shipyard.position]

        # Get friendly ships and enemy ship positions.
        ships = player.get_ships()
        enemy_position_dict = utils.get_enemy_ship_dict(game, player)
        enemy_position_dict = utils.transform_enemy_ship_dict(game, enemy_position_dict)

        # While ships are left in set, do the following:
        ships = set(ships)
        while ships:
            # Find the ship with the lowest amount of initial moves.
            mining_dict =  make_mining_dict(mining_log, t)
            ship = min(ships, key=lambda x: len(get_neighbours(x.position, x.halite_amount, game_map, mining_dict, occupied_log, t)))

            # Extract information from ship.
            ship_log = game_log.player_logs[player.id].ship_logs[ship.id]

            # Calcualte time avaiable for search.
            timeout = (max_time - (timeit.default_timer() - start_time)) / len(ships)

            direction, mining_log, occupied_log = ship_log.objective.execute(game, mining_log, occupied_log, enemy_position_dict, timeout)

            # Append to command queue and remove ship from set.
            command_queue.append(ship.move(direction))
            ships.remove(ship)

        return command_queue

from halite.dtypes import Direction


class Navigator:
    def __init__(self, config):
        self.config = config

    def __call__(self, board, strategy):
        return self.navigate(board, strategy)

    def navigate(self, board, strategy):
        raise NotImplementedError



class DumbNavigator(Navigator):
    def navigate(self, board, strategy):
        for ship in board.ships:
            objective = strategy[ship]
            direction = self.move_towards(ship.pos, objective.pos)
            if direction is not None:
                ship.move(direction)

    def move_towards(self, pos1, pos2):
        dx, dy = pos1.signed_distance2(pos2)
        if abs(dx) >= abs(dy):
            if dx > 0:
                return Direction.east
            elif dx < 0:
                return Direction.west
            else:
                return None
        else:
            if dy > 0:
                return Direction.north
            elif dy < 0:
                return Direction.south
            else:
                return None


"""
==============
Old AStar code
==============

Keeping this around for when the AStarSearch module is revived

"""

# class AStarNavigator(ShipNavigator):

#     def __init__(self, step_penalty, t_max=None, enemy_position_penalty=1000, end_game=False):
#         self.step_penalty = step_penalty
#         if t_max is None:
#             t_max = constants.MAX_TURNS
#         self.t_max = t_max
#         self.enemy_position_penalty = enemy_position_penalty
#         self.end_game = end_game

#     def __repr__(self):
#         return "{}(step_penalty={}, end_game={})".format(self.__class__.__name__, self.step_penalty, self.end_game)


#     def navigate(self, game_map, start_pos, goal_pos, halite_amount, mining_log, occupied_log, enemy_position_dict, t, timeout):
#         """
#         Navigation for individual ship from start_pos to goal_pos.
#         """
#         # Initialise important variables.
#         start = (start_pos, t)

#         # Execute a* search.
#         came_from, cost_so_far, halite_so_far, mining_so_far, goal = a_star_search(game_map=game_map, start_pos=start_pos, goal_pos=goal_pos, halite_amount=halite_amount, mining_log=mining_log, occupied_log=occupied_log, step_penalty=self.step_penalty, enemy_position_dict=enemy_position_dict, enemy_position_penalty=self.enemy_position_penalty, t=t, t_max=self.t_max, timeout=timeout)

#         # Reconstruct information from search.
#         path = reconstruct_path(came_from, start, goal)
#         mining_log = mining_so_far[goal]

#         # If path only contains 1 element, add second element.
#         if len(path) == 1:
#             path.append((start_pos, t + 1))

#         # Get direction to next position in path.
#         next_pos = path[1][0]
#         direction = _get_direction(game_map, start_pos, next_pos)

#         # If is end game, do not occupy position of shipyard.
#         if self.end_game:
#             path = path[:-1]

#         # Add path to occupied_log.
#         add_path_to_occupied(path, occupied_log)

#         return direction, mining_log, occupied_log

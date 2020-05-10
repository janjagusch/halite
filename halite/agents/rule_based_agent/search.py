import logging
import timeit
from collections import Counter
from copy import deepcopy
import heapq
import numpy as np
from hlt.positionals import Position, Direction
import hlt.constants as constants


class PriorityQueue:
    """
    Priority queue class for A* search.
    Taken from https://www.redblobgames.com/pathfinding/a-star/implementation.html.
    """
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def get_heuristic(current, goal, game_map, step_penalty):
    """
    Intelligent heuristic for the A* search.
    Args:
        current: object of class Position, describing current position.
        goal: object of class Position, describing goal position.
        game_map: object of class GameMap, describing game map that current and goal are located on.
        step_penalty: numeric value, that is added for every step between current and goal.
    Returns:
        heuristic (lower bound cost) between current and goal.
    """
    return game_map.calculate_distance(current, goal) * step_penalty


def reconstruct_path(came_from, start, goal):
    """
    Reconstructs path between start and goal.
    Args:
        came_from: dictionary with node visit log, returned by a_star_search().
        start: key in came_from, that you start from.
        goal: key in came_from, that you end at.
    Returns:
        path (list) of came_from values.
    Notes:
        start and goal can be elements of type Position or tuples (Position, t),
        where t is an integer timestep.
    """
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


def make_mining_dict(mining_log, t):
    """Converts mining log at timestep t to mining dict."""
    mining_dict = []
    for k, v in mining_log.items():
        if k < t:
            mining_dict += v
    mining_dict = Counter(mining_dict)
    return mining_dict


def get_cell_value(position, game_map, mining_dict, t):
    """Returns expected value of cell."""
    cell_value = game_map[position].halite_amount
    n_mined = mining_dict[t][position] if t in mining_dict.keys() and position in mining_dict[t].keys() else 0
    for i in range(n_mined):
        cell_value = int(cell_value * (1 - 1 / constants.EXTRACT_RATIO))
    return cell_value


def get_move_cost(cell_value):
    """Returns move cost, given cell value."""
    move_cost = int(cell_value / constants.MOVE_COST_RATIO)
    return move_cost


def get_mining_cost(cell_value, halite_amount):
    """Returns mining reward (negative cost), given cell value and halite amount."""
    mining_cost = max(int(-cell_value / constants.EXTRACT_RATIO), halite_amount - constants.MAX_HALITE)
    return mining_cost


def get_available_directions(game_map, position, occupied_dict, t):
    """Returns available directions (non-occupied) neighbours from position."""
    directions = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    available_directions = [current_direction for current_direction in directions if t not in occupied_dict.keys() or game_map.normalize(position.directional_offset(current_direction)) not in occupied_dict[t]]
    return available_directions


def get_neighbours(position, halite_amount, game_map, mining_dict, occupied_dict, t):
    """Returns feasible neighbours of position."""
    available_directions = get_available_directions(game_map, position, occupied_dict, t)
    cell_value = get_cell_value(position, game_map, mining_dict, t)
    move_cost = get_move_cost(cell_value)
    if halite_amount < move_cost:
        if Direction.Still in available_directions:
            return [game_map.normalize(position.directional_offset(Direction.Still))]
        else:
            return []
    else:
        return [game_map.normalize(position.directional_offset(current_direction)) for current_direction in available_directions]


def update_mining_log(mining_log, position, t):
    """Updates mining log with recently mined positions. This happens inplace."""
    if t not in mining_log.keys():
        mining_log[t] = []
    mining_log[t].append(position)


def add_path_to_occupied(path, occupied_log):
    """Update occupied log."""
    for position, t in path:
        if t not in occupied_log.keys():
            occupied_log[t] = [position]
        else:
            occupied_log[t].append(position)


def get_cost(current_pos, next_pos, halite_amount, mining_dict, game_map, t, enemy_position_dict, enemy_position_penalty):
    """Returns cost at current position."""
    cell_value = get_cell_value(current_pos, game_map, mining_dict, t)
    # If next position is equal to current position, get mining reward.
    if current_pos == next_pos:
        move_cost = get_mining_cost(cell_value, halite_amount)
    # Otherwise, get moving cost.
    else:
        move_cost = get_move_cost(cell_value)
    if (next_pos, t) in enemy_position_dict:
        move_cost += enemy_position_penalty * enemy_position_dict[(next_pos, t)]

    return move_cost


def a_star_search(game_map, start_pos, goal_pos, halite_amount, mining_log, occupied_log, step_penalty, t, t_max, enemy_position_dict, enemy_position_penalty=1000., timeout=0.1):
    """
    Determines optimal path from start to goal, provided game_map and step_penalty.
    Args:
        game_map: object of class GameMap.
        start_pos: object of class Position.
        goal_pos: object of class Position.
        halite_amount: initial halite amout of ship.
        mining_log: log of previous mining activities.
        occupied_log: log of already occupied positions.
        step_penalty: additional cost per move.
        t: current time step.
        t_max: maximum time step.
        timeout: maximum time for search.
    Returns:
        came_from: dictionary of node visits.
        cost_so_far: dictionary of cost.
        halite_so_far: dictionary of final halite.
        mining_so_far: dictionary of mined positions.
        current: current best final position.
    """
    start_time = timeit.default_timer()

    start = (start_pos, t)
    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from = {}
    cost_so_far = {}
    halite_so_far = {}
    mining_so_far = {}

    came_from[start] = None
    cost_so_far[start] = 0
    halite_so_far[start] = halite_amount
    mining_so_far[start] = mining_log

    while not frontier.empty():
        current = frontier.get()
        current_pos, current_t = current
        current_halite = halite_so_far[current]
        current_cost = cost_so_far[current]
        current_mining = mining_so_far[current]
        # Check for stopping conditions.
        if current_pos == goal_pos and current_t != t:
            break
        current_time = timeit.default_timer()
        if current_time - start_time > timeout:
            break
        next_t = current_t + 1
        if next_t == t_max:
            continue
        minig_dict = make_mining_dict(current_mining, next_t)
        neighbours = get_neighbours(current_pos, current_halite, game_map, minig_dict, occupied_log, next_t)
        for next_pos in neighbours:
            next = (next_pos, next_t)
            cost = get_cost(current_pos, next_pos, current_halite, minig_dict, game_map, next_t, enemy_position_dict, enemy_position_penalty)
            next_cost = current_cost + cost + step_penalty
            next_halite = min(constants.MAX_HALITE, current_halite - cost)
            if next not in cost_so_far or next_cost < cost_so_far[next]:
                next_mining = deepcopy(current_mining)
                if current_pos == next_pos:
                    update_mining_log(next_mining, next_pos, next_t)
                cost_so_far[next] = next_cost
                halite_so_far[next] = next_halite
                mining_so_far[next] = next_mining
                heuristic = get_heuristic(next_pos, goal_pos, game_map, step_penalty)
                priority = next_cost + heuristic
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far, halite_so_far, mining_so_far, current

class Board:
    def __init__(self, obs, config):
        self.action = {}
        self.obs = obs
        self.config = config
        size = config.size
        
        self.shipyards = [-1] * size ** 2
        self.shipyards_by_uid = {}
        self.ships = [None] * size ** 2
        self.ships_by_uid = {}
        self.possible_ships = [{} for _ in range(size ** 2)]
        
        for index, player in enumerate(obs.players):
            _, shipyards, ships = player
            for uid, pos in shipyards.items():
                self.shipyards[pos] = index
                self.shipyards_by_uid[uid] = {"player_index": index, "uid": uid, "pos": pos}
            for uid, ship in ships.items():
                pos, ship_halite = ship
                details = {"halite": ship_halite, "player_index": index, "uid": uid, "pos": pos}
                self.ships[pos] = details
                self.ships_by_uid[uid] = details
                for direction in ["NORTH", "EAST", "SOUTH", "WEST"]:
                    self.possible_ships[Board.get_to_pos(size, pos, direction)][uid] = details
    
    @staticmethod
    def get_col_row(size, pos):
        return (pos % size, pos // size)

    @staticmethod
    def get_to_pos(size, pos, direction):
        col, row = Board.get_col_row(size, pos)
        if direction == "NORTH":
            return pos - size if pos >= size else size ** 2 - size + col
        elif direction == "SOUTH":
            return col if pos + size >= size ** 2 else pos + size
        elif direction == "EAST":
            return pos + 1 if col < size - 1 else row * size
        elif direction == "WEST":
            return pos - 1 if col > 0 else (row + 1) * size - 1

    def move(self, ship_uid, direction):
        self.action[ship_uid] = direction
        # Update the board.
        self.__remove_possibles(ship_uid)
        ship = self.ships_by_uid[ship_uid]
        pos = ship["pos"]
        to_pos = Board.get_to_pos(self.config.size, pos, direction)
        ship["pos"] = to_pos
        self.ships[pos] = None
        self.ships[to_pos] = ship
    
    def convert(self, ship_uid):
        self.action[ship_uid] = "CONVERT"
        # Update the board.
        self.__remove_possibles(ship_uid)
        pos = self.ships_by_uid[ship_uid]["pos"]
        self.shipyards[pos] = self.obs.player
        self.ships[pos] = None
        del self.ships_by_uid[ship_uid]
    
    def spawn(self, shipyard_uid):
        self.action[shipyard_uid] = "SPAWN"
        # Update the board.
        temp_uid = f"Spawn_Ship_{shipyard_uid}"
        pos = self.shipyards_by_uid[shipyard_uid]["pos"]
        details = {"halite": 0, "player_index": self.obs.player, "uid": temp_uid, "pos": pos}
        self.ships[pos] = details
        self.ships_by_uid = details
    
    def __remove_possibles(self, ship_uid):
        pos = self.ships_by_uid[ship_uid]["pos"]
        for d in ["NORTH", "EAST", "SOUTH", "WEST"]:
            to_pos = Board.get_to_pos(self.config.size, pos, d)
            del self.possible_ships[to_pos][ship_uid]
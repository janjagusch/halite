from halite.interpreter.exceptions import InvalidConstantError


class _GameConstants:
    @classmethod
    def enum(cls):
        return {
            key: value
            for key, value in vars(cls).items()
            if not key.startswith("__") and not key.endswith("__")
        }

    @classmethod
    def assert_valid(cls, value):
        enum = list(cls.enum().values())
        if value not in enum:
            raise InvalidConstantError(value, enum)


class UnitStatus(_GameConstants):

    ACTIVE = "ACTIVE"
    DESTROYED = "DESTROYED"
    CONVERTED = "CONVERTED"


class UnitType(_GameConstants):

    SHIP = "SHIP"
    SHIPYARD = "SHIPYARD"


class Actions(_GameConstants):

    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"
    CONVERT = "CONVERT"
    SPAWN = "SPAWN"


class Events(_GameConstants):

    MOVED = "MOVED"
    SPAWNED = "SPAWNED"
    CONVERTED = "CONVERTED"
    DEPOSITED = "DEPOSITED"
    MINED = "MINED"
    REGENERATED = "REGENERATED"
    DAMAGED = "DAMAGED"
    DESTROYED = "DESTROYED"


class PlayerStatus(_GameConstants):

    ACTIVE = "ACTIVE"
    LOST = "No potential to gather halite remaining."
    DONE = "DONE"

from dataclasses import dataclass


# TODO Replace this with proper subclasses with methods
@dataclass
class Direction:
    east = "EAST"
    north = "NORTH"
    west = "WEST"
    south = "SOUTH"



@dataclass
class Action:
    spawn = "SPAWN"
    convert = "CONVERT"


class Position(tuple):
    _size: int

    def __new__(cls, *args):
        x, y, size = args
        obj = tuple.__new__(cls, (x,y))
        obj._size = size
        return obj

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def size(self):
        return self._size

    def distance(self, pos):
        return sum(self.distance2(pos))

    def distance2(self, pos):
        return (abs(self.signed_distance_1D(self.x, pos.x, self._size)), 
                abs(self.signed_distance_1D(self.y, pos.y, self._size)))

    def signed_distance2(self, pos):
        return (self.signed_distance_1D(self.x, pos.x, self._size), 
                self.signed_distance_1D(self.y, pos.y, self._size))
    
    @staticmethod
    def signed_distance_1D(x1, x2, size):
        dist = x2-x1
        if abs(dist) > size/2:
            dist = dist - size
        return dist


    def __add__(self, other):
        if other == Direction.north:
            return Position(self.x, (self.y + 1) % self._size, self._size)
        elif other == Direction.south:
            return Position(self.x, (self.y - 1) % self._size, self._size)
        elif other == Direction.east:
            return Position((self.x + 1) % self._size, self.y, self._size)
        elif other == Direction.west:
            return Position((self.x - 1) % self._size, self.y, self._size)
        else:
            raise ValueError("Can only add directions to a position!")
   
    def __repr__(self):
        return f"Position(x={self.x}, y={self.y})"

from common import *

from math import sqrt, pow
from enum import Enum

PLAYER_CAR = "A"
EMPTY_TILE = "o"
WALL_TILE = "x"

class Direction(Enum):
    UP = "w"
    DOWN = "s"
    LEFT = "a"
    RIGHT = "d"

    def getVector(self):
        if self == Direction.UP:
            return Coordinates(0, -1)
        elif self == Direction.DOWN:
            return Coordinates(0, 1)
        elif self == Direction.RIGHT:
            return Coordinates(1,0)
        else:
            return Coordinates(-1, 0)

class Orientation(Enum):
    HORIZONTAL = "y"
    VERTICAL = "x"

    def getDirections(self):
        if self == Orientation.HORIZONTAL:
            return [Direction.LEFT, Direction.RIGHT]
        else:
            return [Direction.UP, Direction.DOWN]

class Car():
    def __init__(self, color: str, coords):
        self.color = color
        self.coords = coords

    def __repr__(self):
        strlst = ["(" + str(c.x) + ", " + str(c.y) + ")" for c in self.coords]
        return "[" + self.color + " " + ' '.join(strlst) + "]"

    @property
    def orientation(self):
        if self.coords[0].x == self.coords[1].x:
            return Orientation.VERTICAL
        return Orientation.HORIZONTAL

    @property
    def constCoord(self):
        if self.orientation == Orientation.VERTICAL:
            return self.coords[0].x
        return self.coords[0].y

    @property
    def length(self):
        return len(self.coords)

class Map2(Map):
    def __init__(self, txt: str):
        super().__init__(txt)
        self.gridstr = txt.split(" ")[1]

    def getCars(self):
        """
        getCars(map)
            @map: Map2

        returns all cars in map
        returns carlist: lst<Car>
        """
        colors = {cc for x, y, cc in self.coordinates}
        cars = [Car(cc, self.piece_coordinates(cc)) for cc in colors if cc not in [EMPTY_TILE, WALL_TILE]]
        return cars

    def getTile(self, coords: Coordinates):
        """
        getTile(coords)
            @coords: Coordinates

        returns info about tile at given coordinates
        returns (tileidentifier: str, coords: Coordinates)
        """
        try:
            tile = super().get(coords)
        except MapException:
            tile = WALL_TILE
        return (tile, coords)

    def neighbourTile(self, car: Car, direction: Direction, offset: int = 1):
        """
        neighbourTile(self, car, direction, offset)
            @car: Car
            @direction: Direction
            @offset: int (default value = 1)

        returns info about the tiles right next to car
        specify offset to go to second, third, ... neighbours
        if car is vertical, returns top and bottom tiles
        if car is horizontal, returns right and left tiles
        returns (tileidentifier: str, coords: Coordinates)
        """
        assert (car.orientation == Orientation.VERTICAL) == (direction == Direction.UP or direction == Direction.DOWN)
        assert (car.orientation == Orientation.HORIZONTAL) == (direction == Direction.RIGHT or direction == direction.LEFT) 
        
        if direction == Direction.RIGHT:
            values = [c.x for c in car.coords]
            x = max(values) + offset
            y = car.coords[0].y
            return self.getTile(Coordinates(x, y))
        elif direction == Direction.UP:
            x = car.coords[0].x
            values = [c.y for c in car.coords]
            y = min(values) - offset
            return self.getTile(Coordinates(x, y))
        elif direction == Direction.DOWN:
            x = car.coords[0].x
            values = [c.y for c in car.coords]
            y = max(values) + offset
            return self.getTile(Coordinates(x, y))
        else:
            values = [c.x for c in car.coords]
            x = min(values) - offset
            y = car.coords[0].y
            return self.getTile(Coordinates(x, y))

    def tryMove(self, car: Car, direction: Direction):
        """
        tryMove(car, direction)
            @car: Car
            @direction: Direction

        checks if a move is valid
        returns True or False
        """
        if self.neighbourTile(car, direction)[0] == EMPTY_TILE:
            return True
        return False

    def changeMap(self, carcolor: str, direction: Direction):
        new_map = Map2(self.__repr__())
        new_map.move(carcolor, direction.getVector())
        return new_map

    def isSolution(self):
        playercoords = self.piece_coordinates(PLAYER_CAR)[0]

        if all([tile in [EMPTY_TILE, PLAYER_CAR] for x, y, tile in self.coordinates if y == playercoords.y and x > playercoords.x]):
            return True
        return False

    def heuristic(self):
        playercoords = self.piece_coordinates(PLAYER_CAR)[0]
        blockingcars = [tile for x, y, tile in self.coordinates if y == playercoords.y and x > playercoords.x if tile not in [EMPTY_TILE, WALL_TILE, PLAYER_CAR ]]

        neighbours = [self.neighbourTile(Car(tile, self.piece_coordinates(tile)), Direction.UP) for tile in blockingcars]
        neighbours += [self.neighbourTile(Car(tile, self.piece_coordinates(tile)), Direction.DOWN) for tile in blockingcars]

        blockingblockingcars = [tile for tile in neighbours if tile not in [EMPTY_TILE, WALL_TILE, PLAYER_CAR]]
        return len(blockingcars) + len(blockingblockingcars)

    def print_grid(self):
        line = ""
        for i, pos in enumerate(self.gridstr):
            line += pos + " "
            if (i + 1) % self.grid_size == 0:
                print(line)
                line = ""
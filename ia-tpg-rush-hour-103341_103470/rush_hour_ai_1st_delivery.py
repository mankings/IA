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
            return Coordinates(-1, 0)
        elif self == Direction.DOWN:
            return Coordinates(1, 0)
        elif self == Direction.RIGHT:
            return Coordinates(0, 1)
        else:
            return Coordinates(0, -1)

    def flip(self):
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.RIGHT:
            return Direction.LEFT
        else:
            return Direction.RIGHT

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

    def getBlockData(self, blockingcar: Car, blockedcar: Car = None, direction: Direction = None):
        """
        getBlockData(self, blockedcar, blockingcar, direction)
            @blockedcar: Car
            @blockingcar: Car
            @direction: Direction

        returns blockedcar's coordinates where block happens.
        if a move direction is provivided, also returns how many moves needed to unblock
        returns blockcoords: Coordinates, movesneeded: int | None
        """   
        if blockingcar.color == PLAYER_CAR and blockedcar == None:
            player_car = Car(PLAYER_CAR, super.piece_coordinates(PLAYER_CAR))
            blockcoords = Coordinates(max([c.x for c in player_car.coords]), player_car.coords[0].y)
            movesneeded = 5 - blockcoords.x
            return blockcoords, movesneeded

        pairs = [(c1, c2) for c1 in blockedcar.coords for c2 in blockingcar.coords]
        sortedpairs = sorted(pairs, key=lambda point: sqrt(pow(point[0].x - point[1].x, 2) + pow(point[0].y - point[1].y, 2)))
        blockcoords = sortedpairs[0][0]
        if direction is None:
            return blockcoords, None

        movesneeded = 0
        if direction == Direction.RIGHT:
            x = blockedcar.constCoord
            movesneeded = len([c for c in blockingcar.coords if c.x >= x])
        elif direction == Direction.UP:
            y = blockedcar.constCoord
            movesneeded = len([c for c in blockingcar.coords if c.y <= y])
        elif direction == Direction.DOWN:
            y = blockedcar.constCoord
            movesneeded = len([c for c in blockingcar.coords if c.y >= y])
        else: # direction.LEFT
            x = blockedcar.constCoord
            movesneeded = len([c for c in blockingcar.coords if c.x <= x])

        return blockcoords, movesneeded

    def getFirstDirection(self, blockingcar: Car, blockedcar: Car = None):
        """
        chooseBestDirection(blockingcar, blockedcar)
            @blockingcar: Car
            @blockedcar: Car

        chooses best direction to pursue the outcome from given a block happening between both cars
        has no lookahead on the cars blocking blockingcar (for now, maybe (?))
        returns direction: Direction
        """
        # if player car, always check right first, because that is our goal
        if blockingcar.color == PLAYER_CAR and blockedcar == None:
            return Direction.RIGHT

        blockcoords, movesneeded = self.getBlockData(blockingcar, blockedcar)
        if blockingcar.orientation == Orientation.HORIZONTAL:
            # go right or left?
            # if blocking car length is 3, there is only one side to move as to unblock
            if blockingcar.length == 3:
                return Direction.LEFT if blockcoords.x > 2 else Direction.RIGHT

            # if blocking car length is 2, there might be two directions to which we can go
            # so we have to check where we to go
            else:
                # if block happens in left side of the screen, we go right
                if blockcoords.x < 2:
                    return Direction.RIGHT

                # if block happend in right side of the screen, we go left
                elif blockcoords.x > 3:
                    return Direction.LEFT

                # else block happens in the middle, we go to where we need to move less
                #
                #    +          + 
                #    +    OR    +       ++ - blocked car
                #   oo          oo      oo - blocking car 
                # 
                # in instances like these, we can unblock by moving 1 step in one direction, but 2 in the other direction
                # we prioritize the one with less moves needed
                else:
                    return Direction.LEFT if all([coords.x <= blockcoords.x for coords in blockingcar.coords]) else Direction.RIGHT

        else: # vertical car
            # go up or down?
            # if blocking car length is 3, there is only one side to move as to unblock
            if blockingcar.length == 3:
                return Direction.UP if blockcoords.y > 2 else Direction.DOWN
            
            # if blocking car length is 2, there might be two directions to which we can go
            # so we have to check where we to go
            else:
                # if block happens at the top of the screen, we go down
                if blockcoords.y < 2:
                    return Direction.DOWN

                # elif block happens at the bottom of the screen, we go up
                elif blockcoords.y > 3:
                    return Direction.UP

                # in instances like these, we can unblock by moving 1 step up or down, but 2 in the other direction
                #
                #     o    OR    ++o      ++ - blocked car
                #   ++o            o      oo - blocking car 
                # 
                # in instances like these, we can unblock by moving 1 step in one direction, but 2 in the other direction
                # we prioritize the one with less moves needed
                else:
                    return Direction.UP if all([coords.y <= blockcoords.y for coords in blockingcar.coords]) else Direction.DOWN   

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

    def changeMap(self, node, carcolor, direction):
        pieces, grid, movements = node.map.__repr__().split(" ")
        carcolor_coordinates = self.piece_coordinates(carcolor)

        if direction == Direction.RIGHT:
            back_coordinate = carcolor_coordinates[0].x + (6*carcolor_coordinates[0].y)
            front_coordinate = carcolor_coordinates[-1].x + 1 + 6 * (carcolor_coordinates[-1].y)

        elif direction == Direction.LEFT:
            back_coordinate = carcolor_coordinates[-1].x + (6 * carcolor_coordinates[-1].y)
            front_coordinate = carcolor_coordinates[0].x - 1 + (6 * carcolor_coordinates[0].y)

        elif direction == Direction.DOWN:
            back_coordinate = carcolor_coordinates[0].x + (6* carcolor_coordinates[0].y)
            front_coordinate = carcolor_coordinates[-1].x + (6 * (carcolor_coordinates[-1].y + 1))
        
        elif direction == Direction.UP:
            back_coordinate = carcolor_coordinates[-1].x + (6 * carcolor_coordinates[-1].y)
            front_coordinate = carcolor_coordinates[0].x + (6 * (carcolor_coordinates[0].y - 1))

        grid = grid[:back_coordinate] + EMPTY_TILE + grid[back_coordinate + 1:]
        grid = grid[:front_coordinate] + carcolor + grid[front_coordinate + 1:]


        new_map = Map2(pieces + " " + grid + " " + movements)

        return new_map

    def isSolution(self):
        playercoords = self.piece_coordinates(PLAYER_CAR)[0]

        print([tile for x, y, tile in self.coordinates if y == playercoords.y and x > playercoords.x])
        print([tile in [EMPTY_TILE, PLAYER_CAR] for x, y, tile in self.coordinates if y == playercoords.y and x > playercoords.x])

        if all([tile in [EMPTY_TILE, PLAYER_CAR] for x, y, tile in self.coordinates if y == playercoords.y and x > playercoords.x]):
            return True
        return False

    def findChanges(self, newmap):
        pass

class RushHourDomain:
    def __init__(self, dimensions):
        self.game_width = dimensions[0]
        self.game_height = dimensions[1]
        self.level = 0

    # lista de accoes possiveis num estado
    def actions(self, map: Map2):
        cars = map.getCars()
        allmoves = [(car, direction) for car in cars for direction in Orientation.getDirections(car.orientation)]
        possiblemoves = [(car,direction) for (car,direction) in allmoves if map.tryMove(car, direction)]

        return possiblemoves

    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, map: Map2, move):
        car = move[0]
        direction = move[1]
        map.move(car, direction.getVector())
        return map

class RushHourLevel:
    def __init__(self, domain: RushHourDomain, initialmap: Map2):
        self.domain = domain
        self.initialmap = initialmap
 
    def goal_test(self, _map: Map2):
        return _map.isSolution()

class RushHourNode:
    def __init__(self, _map: Map2, move= None, parent=None, visited_grids=[]):
        self.parent = parent
        self.map = _map
        self.move = move
        self.visited_grids = visited_grids

    def __str__(self):
        return "node{" + str(self.grid) + "," + str(self.move) + "}"
    
    def __repr__(self):
        return str(self)

class RushHourTree:
    def __init__(self, level: RushHourLevel, strategy='breadth'):
        self.level = level
        root = RushHourNode(level.initialmap, visited_grids=[level.initialmap.gridstr])
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.problem = level.domain
        self.n = 0

    # returns what moves lead from initialmap to node
    def get_moves(self, node):
        if node.parent == None:
            return []
        moves = self.get_moves(node.parent)
        moves.append(node.move)
        return moves

    # search for the solution using the tree
    def search(self, limit=None):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)

            if self.level.goal_test(node.map):
                print("solution!")
                self.solution = node
                self.plan = self.get_moves(node)
                return self.plan

            lnewnodes = []

            for move in self.problem.actions(node.map):
                car = move[0]

                direction = move[1]

                new_map = node.map.changeMap(node, car.color, direction) 

                if new_map.grid not in node.visited_grids:
                    new_visited_grids = node.visited_grids
                    new_visited_grids.append(new_map.grid)
                    newnode = RushHourNode(new_map, (car.color, direction), node, new_visited_grids)
                    lnewnodes.append(newnode)

            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        def costFunc(node):
            return node.cost
        
        def heuristicFunc(node):
            return node.heuristic

        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes

class Bot():
    def __init__(self, state):
        self.game_width = state['dimensions'][0]
        self.game_height = state['dimensions'][1]

        self.map = Map2(state['grid'])
        self.level = RushHourLevel(RushHourDomain(state['dimensions']), self.map)
        self.level_state = None

    def moveCursor(self, coords: Coordinates):
        """
        moveCursor(self, coords)
            @coords: Coordinates
        
        appends the input needed to move the cursor to given coordinates
        returns void
        """
        if self.cursorcoords == coords:
            return
        
        x, y = (self.cursorcoords.x - coords.x, self.cursorcoords.y - coords.y)

        for i in range(abs(x)):
            if x > 0: self.moves.append(Direction.LEFT.value)
            else: self.moves.append(Direction.RIGHT.value)
        for i in range(abs(y)):
            if y > 0: self.moves.append(Direction.UP.value)
            else: self.moves.append(Direction.DOWN.value)
        
    def selectCar(self, carcolor):
        """
        selectCar(self, carcolor)
            @carcolor: str

        appends the input needed to select given car
        returns void
        """
        if self.map.get(Coordinates(self.cursor[0], self.cursor[1])) == carcolor:
            if self.selected:
                return
            else:
                self.moves.append(" ")
                return

        if self.selected:
            self.moves.append(" ")

        coords = self.map.piece_coordinates(carcolor)
        sortedcoords = sorted(coords, key=lambda c : sqrt(pow(c.x - self.cursor[0], 2) + pow(c.y - self.cursor[1], 2)))
        optimalcoords = sortedcoords[0]
        self.moveCursor(optimalcoords)
        self.moves.append(" ")

    def moveCar(self, carcolor, direction: Direction):
        """
        moveCar(self, carcolor, direction)
            @carcolor: str
            @direction: Direction

        appends the input needed to select and move the car in given direction
        returns void
        """
        self.selectCar(carcolor)
        self.moves.append(direction.value)

    def run(self, state):
        self.game_speed = state["game_speed"]
        
        self.cursor = state["cursor"]
        self.cursorcoords = Coordinates(self.cursor[0], self.cursor[1])
        self.selected = state["selected"]

        self.map = Map2(state['grid'])

        if self.level_state != state["level"]:
            print("level change!")
            self.level = RushHourLevel(RushHourDomain([self.game_width,self.game_height]), self.map)
            self.tree = RushHourTree(self.level)
            self.level_state = state["level"]
            
            self.moves = []
            actions = self.tree.search()
            for (car, direction) in actions:
                self.moveCar(car, direction)


        if self.map.gridstr not in self.tree.solution.visited_grids and not self.map.isSolution():
            print("crazy car ?") 
            self.moves = []
            actions = self.tree.search()
            for (car, direction) in actions:
                self.moveCar(car, direction)


        if self.moves != []:
            return self.moves.pop(0)
        elif self.map.isSolution():
            self.moveCar(PLAYER_CAR, Direction.RIGHT)
            return self.moves.pop(0)
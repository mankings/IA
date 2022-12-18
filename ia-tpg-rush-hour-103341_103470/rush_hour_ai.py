from problem import *

class Bot():
    def __init__(self, dimensions, grid):
        self.game_width = dimensions[0]
        self.game_height = dimensions[1]
        self.level = RushHourLevel(RushHourDomain(dimensions), Map2(grid))
        self.domain = RushHourDomain(dimensions)

        self.level_state = None

        self.last_grid = None
        self.last_move = None

        self.needToCalc = False

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
            if x > 0:
                self.moves.append(Direction.LEFT.value)
                self.cursorcoords.x -= 1
            else:
                self.moves.append(Direction.RIGHT.value)
                self.cursorcoords.x += 1
        for i in range(abs(y)):
            if y > 0:
                self.moves.append(Direction.UP.value)
                self.cursorcoords.y -= 1
            else:
                self.moves.append(Direction.DOWN.value)
                self.cursorcoords.y += 1
        
    def selectCar(self, carcolor):
        """
        selectCar(self, carcolor)
            @carcolor: str

        appends the input needed to select given car
        returns void
        """
        if self.map.get(self.cursorcoords) == carcolor:
            if self.selected == carcolor:
                return
            else:
                self.moves.append(" ")
                self.selected = carcolor
                return

        if self.selected:
            self.moves.append(" ")
            self.selected = ''

        coords = self.map.piece_coordinates(carcolor)
        sortedcoords = sorted(coords, key=lambda c: sqrt(pow(c.x - self.cursorcoords.x, 2) + pow(c.y - self.cursorcoords.y, 2)))
        optimalcoords = sortedcoords[0]
        self.moveCursor(optimalcoords)
        self.moves.append(" ")
        self.selected = carcolor

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
        self.map = self.map.changeMap(carcolor, direction)
        self.cursorcoords.x += direction.getVector().x
        self.cursorcoords.y += direction.getVector().y

    def search(self):
        """
        search(self)

        creates a new search tree for current state and searches it
        returns move list to solution
        """
        self.level = RushHourLevel(RushHourDomain([self.game_width,self.game_height]), Map2(self.grid))
        self.tree = RushHourTree(self.level, strategy='greedy')
        self.moves = []
        self.plan = []
        print("searching...", end=" ")
        return self.tree.search()

    def appendInputs(self, moves, rightSide=False):
        """
        appendInputs(self, moves, rightSide)
            moves: lst
            rightSide: bool = False

        for each move, appends it's respective inputs to self.moves as to get to solution
        returns void
        """
        if not rightSide:
            for (car, direction) in moves:
                _len = len(self.moves)
                self.moveCar(car, direction)
                self.plan.append(((car, direction), len(self.moves) - _len))
        else:
            oldmoves = [i[0] for i in self.plan]
            self.moves = []
            self.plan = []
            for (car, direction) in moves + oldmoves:
                _len = len(self.moves)
                self.moveCar(car, direction)
                self.plan.append(((car, direction), len(self.moves) - _len))

    def run(self, state):
        print()
        print("  running.....")
        def calc_reset():
            self.inputcntr = 0
            self.last_move = None
            self.last_inputs = 0
            self.needToCalc = True

        def input_reset():
            pass

        self.game_speed = state["game_speed"]

        self.selected = state["selected"]
        self.cursor = state["cursor"]
        self.cursorcoords = Coordinates(self.cursor[0], self.cursor[1])

        self.grid = state['grid']
        self.map = Map2(self.grid)
        
        if self.level_state != state["level"]:
            print("level change!")

            self.level_state = state["level"]
            self.last_grid = None
            calc_reset()

        if self.last_grid != None and self.last_grid != state["grid"]:
            print("grid change!")
            last_map = Map2(self.last_grid)
            if self.last_move == None:
                crazycars = [c[2] for c in self.map.coordinates if c not in last_map.coordinates]
                if crazycars != []:
                    print("crazy car1!", crazycars)
                    print("last_move:", self.last_move)
                    calc_reset()
            else:
                if last_map.tryMove(Car(self.last_move[0], last_map.piece_coordinates(self.last_move[0])), self.last_move[1]):
                    expected = Map2(last_map.__repr__())
                    expected = expected.changeMap(self.last_move[0], self.last_move[1])
                    crazycars = [c[2] for c in self.map.coordinates if c not in expected.coordinates and c[2] != self.last_move[0]]
                    if crazycars != []:
                        print("crazy car2!", crazycars)
                        print("last_move:", self.last_move)
                        calc_reset()
                else:                    
                    crazycars = [c[2] for c in self.map.coordinates if c not in last_map.coordinates]
                    if crazycars != []:
                        print("crazy car1!", crazycars)
                        print("last_move:", self.last_move)
                        calc_reset()

        if self.map.isSolution() or self.needToCalc:
            moves = self.search()
            self.appendInputs(moves)
            self.needToCalc = False

        if self.moves != [] and self.plan != []:
            input = self.moves.pop(0)
            if state["selected"] != '' and input != ' ':
                self.last_move, self.last_inputs = self.plan.pop(0)
            else:
                self.last_move = None

            self.last_grid = state["grid"]
            return input
        else: calc_reset()
            
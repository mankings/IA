from classes import *

class RushHourDomain:
    def __init__(self, dimensions):
        self.game_width = dimensions[0]
        self.game_height = dimensions[1]
        self.level = 0

    # lista de accoes possiveis num estado
    def actions(self, map: Map2):
        cars = map.getCars()
        allmoves = [(car, direction) for car in cars for direction in Orientation.getDirections(car.orientation)]
        possiblemoves = [(car, direction) for (car, direction) in allmoves if map.tryMove(car, direction)]

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
    def __init__(self, _map: Map2, move= None, parent=None, heuristic=0, depth=0):
        self.parent = parent
        self.map = _map
        self.move = move
        self.depth = depth
        self.heuristic = heuristic

    def __str__(self):
        return "node{" + str(self.map.gridstr) + "," + str(self.move) + "}"
    
    def __repr__(self):
        return str(self)

class RushHourTree:
    def __init__(self, level: RushHourLevel, strategy='breadth'):
        self.level = level
        root = (level.initialmap, None, None, level.initialmap.heuristic(), 0)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.problem = level.domain
        self.n = 0
        self.visited_grids = [level.initialmap.gridstr]

    # returns what moves lead from initialmap to node
    def get_moves(self, node):
        if node[2] == None:
            return []
        moves = self.get_moves(node[2])
        moves.append(node[1])
        return moves

    # search for the solution using the tree
    def search(self, limit=None):
        total_nodes = 0
        heuristic_sum = 0

        while self.open_nodes != []:
            node = self.open_nodes.pop(0)

            if self.level.goal_test(node[0]):
                self.solution = node
                if node[2] == None:
                    return [(PLAYER_CAR, Direction.RIGHT)]
                print("solution!")
                print("total nodes:", total_nodes)
                print("heuristic_avg:", heuristic_sum/total_nodes)
                print("solution depth:", node[4])
                self.plan = self.get_moves(node)  
                return self.plan

            lnewnodes = []
            for move in self.problem.actions(node[0]):
                car = move[0]
                direction = move[1]
                new_map = node[0].changeMap(car.color, direction)
                if new_map.grid not in self.visited_grids:
                    heuristic = new_map.heuristic()
                    depth = node[4] + 1
                    self.visited_grids.append(new_map.grid)
                    newnode = (new_map, (car.color, direction), node, heuristic, depth)
                    lnewnodes.append(newnode)
                    total_nodes += 1
                    heuristic_sum += heuristic

            self.add_to_open(lnewnodes)
        return None 

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node[3])
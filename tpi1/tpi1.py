from tree_search import *
from cidades import *
from blocksworld import *


def func_branching(connections, coordinates):
    branches = [len([a for a, b, c in connections if a == city or b == city]) for city in coordinates.keys()]
    branching_factor = sum(branches) / len(branches)
    return branching_factor - 1

class MyCities(Cidades):
    def __init__(self, connections, coordinates):
        super().__init__(connections, coordinates)
        self.branching_factor = func_branching(connections, coordinates)

class MySTRIPS(STRIPS):
    def __init__(self, optimize=False):
        super().__init__(optimize)

    def simulate_plan(self, state, plan):
        if plan == []:
            return state
        
        operator = plan.pop(0)
        if all([pc in state for pc in operator.pc]):
            state = [pred for pred in state if pred not in operator.neg]
            state.extend(operator.pos)
        else:
            print(f"ERROR: Couldn't go past\n", state, "\nbecause the pre-conditions\n", operator.pc, "\nare not present in this state.")
            return

        return self.simulate_plan(state, plan)

class MyNode(SearchNode):
    def __init__(self, state, parent, cost=0, heuristic=0, depth=0):
        super().__init__(state,parent)
        self.cost = cost
        self.heuristic = heuristic
        self.depth = depth

class MyTree(SearchTree):
    def __init__(self, problem, strategy='breadth', optimize=0, keep=0.25): 
        self.optimize = optimize

        if self.optimize == 0:
            super().__init__(problem, strategy)
            root = MyNode(problem.initial, None)   
        elif self.optimize == 1:
            super().__init__(problem, strategy)
            root = (problem.initial, None, 0, 0, 0)
        elif self.optimize == 2:
            super().__init__(None, strategy)
            self.problem = problem[0]
            self.initial = problem[1]
            self.goal = problem[2]
            root = (self.initial, None, 0, 0, 0)
        elif self.optimize == 4:
            super().__init__(None, strategy)
            self.problem = problem[0]
            self.initial = problem[1]
            self.goal = problem[2]
            root = (self.initial, None, 0, 0, 0)
            self.existing_states = []

        self.keep = keep
        self.all_nodes = [root]
        self.open_nodes = [0]

    def astar_add_to_open(self, lnewnodes):
        if self.optimize == 0:
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda i: self.all_nodes[i].cost + self.all_nodes[i].heuristic)
        else:
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda i: self.all_nodes[i][2] + self.all_nodes[i][3])

    # remove a fraction of open (terminal) nodes
    # with lowest evaluation function
    # (used in Incrementally Bounded A*)
    def forget_worst_terminals(self):
        nodes = [self.all_nodes[i] for i in self.open_nodes]

        if self.optimize == 0:
            terminal_depths = [node.depth for node in nodes]
            branching = self.problem.domain.branching_factor
        elif self.optimize == 1:
            terminal_depths = [node[4] for node in nodes]
            branching = self.problem.domain.branching_factor
        else:
            terminal_depths = [node[4] for node in nodes]
            branching = self.problem[5]

        avg_depth = sum(terminal_depths)/len(terminal_depths)
        keep_amount = math.trunc(self.keep * math.pow(branching, avg_depth)) + 1
        del self.open_nodes[keep_amount:]

    def get_path(self, node):
        if self.optimize == 0:
            if node.parent == None:
                return [node.state]
            path = self.get_path(self.all_nodes[node.parent])
            path += [node.state]
            return(path)

        if node[1] == None:
            return [node[0]]
        path = self.get_path(self.all_nodes[node[1]])
        path += [node[0]]
        return(path)

    # procurar a solucao
    def search2(self):
        if self.optimize == 0:
            while self.open_nodes != []:
                nodeID = self.open_nodes.pop(0)
                node = self.all_nodes[nodeID]
                if self.problem.goal_test(node.state):
                    self.solution = node
                    self.terminals = len(self.open_nodes) + 1
                    return self.get_path(node)
                lnewnodes = []
                self.non_terminals += 1
                for a in self.problem.domain.actions(node.state):
                    newstate = self.problem.domain.result(node.state, a)
                    if newstate not in self.get_path(node):
                        cost = node.cost + self.problem.domain.cost(node.state, (node.state, newstate))
                        heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                        depth = node.depth + 1
                        newnode = MyNode(newstate, nodeID, cost, heuristic, depth)
                        lnewnodes.append(len(self.all_nodes))
                        self.all_nodes.append(newnode)
                self.add_to_open(lnewnodes)
                if self.strategy == 'IBA*':
                    self.forget_worst_terminals()
            return None

        if self.optimize == 1:
            while self.open_nodes != []:
                nodeID = self.open_nodes.pop(0)
                node = self.all_nodes[nodeID]
                if self.problem.goal_test(node[0]):
                    self.solution = node
                    self.terminals = len(self.open_nodes) + 1
                    return self.get_path(node)
                lnewnodes = []
                self.non_terminals += 1
                for a in self.problem.domain.actions(node[0]):
                    newstate = self.problem.domain.result(node[0], a)
                    if newstate not in self.get_path(node):
                        cost = node[2] + self.problem.domain.cost(node[0], (node[0], newstate))
                        heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                        depth = node[4] + 1
                        newnode = (newstate, nodeID, cost, heuristic, depth)
                        lnewnodes.append(len(self.all_nodes))
                        self.all_nodes.append(newnode)
                self.add_to_open(lnewnodes)
                if self.strategy == 'IBA*':
                    self.forget_worst_terminals()
            return None

        if self.optimize == 2:
            while self.open_nodes != []:
                nodeID = self.open_nodes.pop(0)
                node = self.all_nodes[nodeID]
                if self.problem[4](node[0], self.goal):
                    self.solution = node
                    self.terminals = len(self.open_nodes) + 1
                    return self.get_path(node)
                lnewnodes = []
                self.non_terminals += 1
                for a in self.problem[0](node[0]):
                    newstate = self.problem[1](node[0], a)
                    if newstate not in self.get_path(node):
                        cost = node[2] + self.problem[2](node[0], (node[0], newstate))
                        heuristic = self.problem[3](newstate, self.goal)
                        depth = node[4] + 1
                        newnode = (newstate, nodeID, cost, heuristic, depth)
                        lnewnodes.append(len(self.all_nodes))
                        self.all_nodes.append(newnode)
                self.add_to_open(lnewnodes)
                if self.strategy == 'IBA*':
                    self.forget_worst_terminals()
            return None

        if self.optimize == 4:
            while self.open_nodes != []:
                nodeID = self.open_nodes.pop(0)
                node = self.all_nodes[nodeID]
                if self.problem[4](node[0], self.goal):
                    self.solution = node
                    self.terminals = len(self.open_nodes) + 1
                    return self.get_path(node)
                lnewnodes = []
                self.non_terminals += 1
                for a in self.problem[0](node[0]):
                    newstate = self.problem[1](node[0], a)
                    if newstate not in self.get_path(node):
                        cost = node[2] + self.problem[2](node[0], (node[0], newstate))
                        heuristic = self.problem[3](newstate, self.goal)
                        depth = node[4] + 1
                        newnode = (newstate, nodeID, cost, heuristic, depth)

                        if newstate in self.existing_states:
                            oldnode = [node for node in self.all_nodes if node[0] == newnode[0]][0]
                            if newnode[2] < oldnode[2]:
                                idx = self.all_nodes.index(oldnode)
                                self.all_nodes[idx] = newnode
                                if idx not in self.open_nodes and idx not in lnewnodes:
                                    lnewnodes.append(idx)
                        else:
                            self.existing_states.append(newstate)
                            lnewnodes.append(len(self.all_nodes))
                            self.all_nodes.append(newnode)
                self.add_to_open(lnewnodes)
                if self.strategy == 'IBA*':
                    self.forget_worst_terminals()
            return None

    def pilisse(self, node):
        # check if state exists
        #   if yes, keep the one with lowest cost (discard children too, if any)
        # if doesnt exist, keep node
        pass

# If needed, auxiliary functions can be added
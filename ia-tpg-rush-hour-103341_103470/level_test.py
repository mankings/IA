from rush_hour_ai import *
from time import time

SOLVE_LIST = [22]

def main():
    with open('levels.txt', 'r') as f:
        levels = f.readlines()

    
    timesum = 0

    for i, l in enumerate(levels):
        #if i + 1 in SOLVE_LIST:
        t = solve(l)
        timesum += t

    print("done, total time:", timesum)


def solve(l):
    ldata = l.rstrip().split(" ")
    grid_size = math.sqrt(len(ldata[1]))

    initialmap = Map2(l.rstrip())
    domain = RushHourDomain([grid_size, grid_size])
    level = RushHourLevel(domain, initialmap)
    tree = RushHourTree(level, 'greedy')

    print("\nlevel:", l.split(" ")[0], end = ", ")
    t0 = time()
    tree.search()
    t = time() - t0
    print("time taken:", t)
    return t

if __name__ == "__main__":
    main()
import os, pygame, time, random, math
from copy import deepcopy
from pprint import pprint
import numpy as np
import _2048
from _2048.game import Game2048
from _2048.manager import GameManager

EVENTS = [
    pygame.event.Event(pygame.KEYDOWN,{'key': pygame.K_UP}),
    pygame.event.Event(pygame.KEYDOWN,{'key': pygame.K_DOWN}),
    pygame.event.Event(pygame.KEYDOWN,{'key': pygame.K_LEFT}),
    pygame.event.Event(pygame.KEYDOWN,{'key': pygame.K_RIGHT})
]


CELLS =[
    [(r,c) for c in range(4) for r in range(4)],
    [(r,c) for r in range(4) for r in range(4 - 1, -1, -1)],
    [(r,c) for c in range(4) for r in range(4 - 1, -1, -1)],
    [(r,c) for r in range(4) for r in range(4)]
]

GET_DELTAS =[
    lambda r, c: ((i,c) for i in range (r+1, 4)),
    lambda r, c: ((r,i) for i in range (c-1, -1, -1)),
    lambda r, c: ((i,c) for i in range (r-1, -1, -1)),
    lambda r, c: ((r,i) for i in range (c+1, 4))
]

def free_cells(grid):
    return[(x,y) for x in range(4) for y in range(4) if not grid[y][x]]

def move(grid, action):
    moved, sum = 0,0
    for row, column in CELLS[action]:
        for dr,dc in GET_DELTAS[action](row, column):
            if not grid[row][column] and grid[dr][dc]:
                grid[row][column], grid[dr][dc] = grid[dr][dc], 0
                moved += 1
            if grid [dr][dc]:
                if grid [row][column] == grid[dr][dc]:
                    grid[row][column] *= 2
                    grid[dr][dc] =0
                    sum += grid[row][column]
                    moved += 1
                break
    return grid, moved, sum

def evaluation(grid, n_empty):
    grid = np.array(grid))

    score = 0

    big_t= np.sum(np.power(grid,2))

    smoothness = 0
    s_grid = np.sqrt(grid)

    smoothness -= np.sum(np.abs(s_grid[:,0] - s_grid[:,1]))
    smoothness -= np.sum(np.abs(s_grid[:,1] - s_grid[:,2]))
    smoothness -= np.sum(np.abs(s_grid[:,2] - s_grid[:,3]))
    smoothness -= np.sum(np.abs(s_grid[0,:] - s_grid[1,:]))
    smoothness -= np.sum(np.abs(s_grid[1,:] - s_grid[2,:]))
    smoothness -= np.sum(np.abs(s_grid[2,:] - s_grid[3,:]))

monotonic_up = 0
monotonic_down = 0
monotonic_left = 0
monotonic_right = 0

for x in range(4):
    current = 0
    next = current +1
    while next <4 :
        while next <3 and not grid[next,x]:
            next += 1
        current_cell = grid [current, x]
        current_value = math.log(current_cell,2) if current_cell else 0
        next_cell = grid[next,x]
        next_value = math.log(next_cell, 2) if next_cell else 0
        if current_value > next_value:
            monotonic_up += (next_value- current_value)
        elif next_value > current_value:
            monotonic_down += (current_value - next_value)
        current = next
        next += 1

    monotonic = max(monotonic_up, monotonic_down)+ max(monotonic_left, monotonic_right)

    empty_w = 100000
    smoothness_w=3
    monotonic_w= 10000

    empty_u = n_empty * empty_w
    smooth_u = smoothness ** smoothness_w
    monotonic_u = monotonic * monotonic_w

    score += big_t
    score += empty_u
    score += smooth_u
    score += monotonic_u

    return score

def maximize(grid, depth = 0):
    best_score = -np.inf
    best_action = None

    for action in range(4):
        moved_grid = deepcopy(grid)
        moved_grid, moved, _ = move(moved_grid, action = action)

        if not moved:
            continue

        new_score = add_new_tiles(moved_grid, depth+1)
        if new_score >= best_score:
            best_score = new_score
            best_action = action
    return best_action, best_score

def add_new_tiles(grid, depth=0):
    fcs= free_cells(grid)
    n_empty = len(fcs)

    if n_empty >= 6 and depth >= 3:
        return evaluation(grid, n_empty)
    
    if n_empty >= 0 and depth >= 5:
        return evaluation(grid, n_empty)

    if n_empty ==0 :
        _, new_score = maximize(grid , depth+1)
        return new_score

    sum_score = 0

    for x,y in fcs:
        for v in [2,4]:
            new_grid = deepcopy(grid)
            new_grid[y][x] = v

            _, new_score = maximize(new_grid, depth+1)

            if v ==2:
                new_score *= (0.9/ n_empty)
            else:
                new_score *=(0.1/ n_empty)

            sum_score += new_score
    return sum_score
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

def free_celld(grid):
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

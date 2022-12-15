# df_maze.py
import random
import bpy

import bge
from bge import logic
import GameLogic
from mathutils import Vector
import math

cont = logic.getCurrentController()
own = cont.owner

scene = bge.logic.getCurrentScene()
one_wall = scene.objectsInactive['OneWall']
hall = scene.objectsInactive['Hall']
corner = scene.objectsInactive['Corner']
dead_end = scene.objectsInactive['DeadEnd']
win_obj = scene.objectsInactive['WinObject']

# Create a maze using the depth-first algorithm described at
# https://scipython.com/blog/making-a-maze/
# Christian Hill, April 2017.

class Cell:
    """A cell in the maze.

    A maze "Cell" is a point in the grid which may be surrounded by walls to
    the north, east, south or west.

    """

    # A wall separates a pair of cells in the N-S or W-E directions.
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y):
        """Initialize the cell at (x,y). At first it is surrounded by walls."""

        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}

    def has_all_walls(self):
        """Does this cell still have all its walls?"""

        return all(self.walls.values())

    #UPBGE; used to find dead ends
    def wall_count(self):
        wall_count = 0
        if self.walls['N']:
            wall_count += 1
        if self.walls['E']:
            wall_count += 1
        if self.walls['S']:
            wall_count += 1
        if self.walls['W']:
            wall_count +=1

        return wall_count

    def knock_down_wall(self, other, wall):
        """Knock down the wall between cells self and other."""

        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False


class Maze:
    """A Maze, represented as a grid of cells."""

    def __init__(self, nx, ny, ix=0, iy=0):
        """Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """

        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy
        self.maze_map = [[Cell(x, y) for y in range(ny)] for x in range(nx)]
        
        #UPBGE; 3d vars
        self.cellSize = 14
        self.origin = self.cellSize * self.nx / 2 - self.cellSize / 2

    def cell_at(self, x, y):
        """Return the Cell object at (x,y)."""

        return self.maze_map[x][y]

    def __str__(self):
        """Return a (crude) string representation of the maze."""

        maze_rows = ['-' * self.nx * 2]
        for y in range(self.ny):
            maze_row = ['|']
            for x in range(self.nx):
                if self.maze_map[x][y].walls['E']:
                    maze_row.append(' |')
                else:
                    maze_row.append('  ')
            maze_rows.append(''.join(maze_row))
            maze_row = ['|']
            for x in range(self.nx):
                if self.maze_map[x][y].walls['S']:
                    maze_row.append('-+')
                else:
                    maze_row.append(' +')
            maze_rows.append(''.join(maze_row))
        return '\n'.join(maze_rows)

    """ UPBGE; translate generated maze into instantiated collections """
    def write_to_mesh(self):

        

        for x in range(self.nx):
            for y in range (self.ny):
                cell = self.cell_at(x, y)
                n = cell.walls['N']
                e = cell.walls['E']
                s = cell.walls['S']
                w = cell.walls['W']

                if n and e and s:
                    obj = scene.addObject(dead_end, own)
                elif e and s and w:
                    obj = scene.addObject(dead_end, own)
                    obj.localOrientation = [0, 0, math.radians(270)]
                elif s and w and n:
                    obj = scene.addObject(dead_end, own)
                    obj.localOrientation = [0, 0, math.radians(180)]
                elif w and n and e:
                    obj = scene.addObject(dead_end, own)
                    obj.localOrientation = [0, 0, math.radians(90)]
                elif n and s:
                    obj = scene.addObject(hall, own)
                elif e and w:
                    obj = scene.addObject(hall, own)
                    obj.localOrientation = [0, 0, math.radians(90)]
                elif n and e:
                    obj = scene.addObject(corner, own)
                elif e and s:
                    obj = scene.addObject(corner, own)
                    obj.localOrientation = [0, 0, math.radians(270)]
                elif s and w:
                    obj = scene.addObject(corner, own)
                    obj.localOrientation = [0, 0, math.radians(180)]
                elif w and n:
                    obj = scene.addObject(corner, own)
                    obj.localOrientation = [0, 0, math.radians(90)]
                elif n:
                    obj = scene.addObject(one_wall, own)
                elif e:
                    obj = scene.addObject(one_wall, own)
                    obj.localOrientation = [0, 0, math.radians(270)]
                elif s:
                    obj = scene.addObject(one_wall, own)
                    obj.localOrientation = [0, 0, math.radians(180)]
                elif w:
                    obj = scene.addObject(one_wall, own)
                    obj.localOrientation = [0, 0, math.radians(90)]
                

                obj.position = [x * self.cellSize - self.origin, y * self.cellSize , 0]
                obj.localScale = [1, 1, 1]

    def find_valid_neighbours(self, cell):
        """Return a list of unvisited neighbours to cell."""

        delta = [('W', (-1, 0)),
                 ('E', (1, 0)),
                 ('S', (0, -1)),
                 ('N', (0, 1))]
        neighbours = []
        for direction, (dx, dy) in delta:
            x2, y2 = cell.x + dx, cell.y + dy
            if (0 <= x2 < self.nx) and (0 <= y2 < self.ny):
                neighbour = self.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def make_maze(self):
        # Total number of cells.
        n = self.nx * self.ny
        cell_stack = []
        current_cell = self.cell_at(self.ix, self.iy)
        #UPBGE; Open the maze entrance and setup stored cell var
        current_cell.walls['S'] = False
        furthest_dead_end = current_cell
        # Total number of visited cells during maze construction.
        nv = 1

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:
                 # UPBGE; Store if furthest dead end generated
                if (current_cell.wall_count() == 3):
                    print ("dead end")
                    if (math.dist([current_cell.x, current_cell.y],[self.ix, self.iy]) > math.dist([furthest_dead_end.x, furthest_dead_end.y], [self.ix, self.iy])):
                        furthest_dead_end = current_cell
                        print ("furthest: " + str(furthest_dead_end.x) + ", " + str(furthest_dead_end.y))
            
                # We've reached a dead end: backtrack.
                current_cell = cell_stack.pop()
                continue

            # Choose a random neighbouring cell and move to it.
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            nv += 1


        # UPBGE; spawn in the win object at the furthest dead end
        obj = scene.addObject(win_obj, own)
        obj.position = [furthest_dead_end.x * self.cellSize - self.origin, furthest_dead_end.y * self.cellSize, 0]
        obj.localScale = [1, 1, 1]

#UPBGE
""" Controller activated functionality. Tried really hard to put it in it's own script, 
but we did not figure out how to register this script as a module to be imported elsewhere """
if cont.sensors["Interact"].status == bge.logic.KX_INPUT_JUST_ACTIVATED:
    maze = Maze(7, 7, 3, 0)
    maze.make_maze()

    print(maze)

    maze.write_to_mesh()
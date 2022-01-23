import pygame
from pygame import Rect, Surface
import random

def draw_rect_with_border(screen: Surface, color, rect: Rect, border_width: int, border_color) -> None:
    # Border Rectangle
    pygame.draw.rect(screen, border_color, rect, width=border_width)

    inner_rect = pygame.Rect(rect.left + border_width, rect.top + border_width, rect.width - 2*border_width, rect.height - 2*border_width)

    # Inner Rectangle
    pygame.draw.rect(screen, color, inner_rect)

def save_grid(grid):
    grid = [list(row) for row in grid]
    print("Saving grid...", end="\r")
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            grid[i][j] = grid[i][j].replace("EMPTY", " ").replace("GOAL", "G").replace("WALL", "#").replace("PATH", " ").replace("START", "S")
    out = "\n".join(["".join(row) for row in grid])
    import datetime
    filename = f"{datetime.datetime.now().strftime('DATE_%d_%m_%Y_TIME_%H_%M_%S')}"
    with open(f"./saves/{filename}.txt", "w+") as f:
        f.write(out)
    pygame.time.delay(1000)
    print(" "*20, end="\r")

def load_grid(path, grid_dimensions):
    with open(path, "r") as f:
        grid = f.read()
    m, n = grid_dimensions
    START_POS, GOAL_POS = None, None
    grid = [list(row) for row in grid.split("\n")]

    # Handling grid of weird size
    grid = grid[:m]
    if len(grid) != m:
        grid.extend([["#" for _ in range(n)] for _ in range(m-len(grid))])
    for i, row in enumerate(grid):
        row = row[:n]
        if len(row) != n:
            row.extend(["#" for _ in range(n - len(row))])
        grid[i] = row

    # Converting grid to required format
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "S":
                START_POS = i, j
            if grid[i][j] == "G":
                GOAL_POS = i, j
            grid[i][j] = grid[i][j].replace(" ","EMPTY").replace("G", "GOAL").replace("#", "WALL").replace("S", "START")
    return grid, START_POS, GOAL_POS

def mouse_pos_to_grid_pos(mouse_pos: tuple[int, int], m, n):
    mouseX, mouseY = mouse_pos
    return mouseX//m, mouseY//n

class Node:
    def __init__(self, pos, *, parent, cost=0) -> None:
        self.pos = pos
        self.parent = parent
        self.cost = cost # Cost to reach this node
    
    def get_neighbors(self, grid):
        m, n = len(grid), len(grid[0])
        x, y = self.pos
        neighbors = []
        if x + 1 < m and grid[x + 1][y] != "WALL":
            neighbors.append((x + 1, y))
        if x - 1 >=0 and grid[x - 1][y] != "WALL":
            neighbors.append((x - 1, y))
        if y + 1 < n and grid[x][y + 1] != "WALL":
            neighbors.append((x, y + 1))
        if y - 1 >=0 and grid[x][y - 1] != "WALL":
            neighbors.append((x, y - 1))
        return neighbors

def heuristic_function(pos, GOAL_POS):
    'Uses Manhattan Distance'
    cost = abs(pos[0]-GOAL_POS[0]) + abs(pos[1]-GOAL_POS[1])
    # print(f"POS:<{pos[0], pos[1]}> | GOAL_POS: <{GOAL_POS[0]}, {GOAL_POS[1]}> | COST: {cost}")
    return cost


# Returns Position of all the nodes in path, Path length, visited length
def DFS_greedy(grid, START_POS, GOAL_POS):
    stack = [
        Node(START_POS, parent=None, cost=0)
    ]
    path = []

    visited = set()
    while len(stack) > 0:
        cur = stack.pop()
        visited.add(cur.pos)
        if cur.pos == GOAL_POS:
            tmp = cur
            while tmp.parent is not None:
                path.append(tmp.pos)
                tmp = tmp.parent
            return path[1:], len(visited)
        neighbors = cur.get_neighbors(grid)

        # Sort neigbhors which are closer heuristically (Greedy Approach)
        neighbors.sort(key=lambda x: heuristic_function(x, GOAL_POS), reverse=True)

        # Neigbhors are added to the stack such that closest neighbors are at the top of the stack.
        for n in neighbors:
            if n not in visited:
                stack.append(Node(n, parent=cur, cost=cur.cost + 1))
    return None

def DFS_random(grid, START_POS, GOAL_POS):
    stack = [
        Node(START_POS, parent=None, cost=0)
    ]
    path = []

    visited = set()
    while len(stack) > 0:
        cur = stack.pop()
        visited.add(cur.pos)
        if cur.pos == GOAL_POS:
            tmp = cur
            while tmp.parent is not None:
                path.append(tmp.pos)
                tmp = tmp.parent
            return path[1:], len(visited)
        neighbors = cur.get_neighbors(grid)

        # Select neighbor randomly (Random)
        random.shuffle(neighbors)

        for n in neighbors:
            if n not in visited:
                stack.append(Node(n, parent=cur, cost=cur.cost + 1))
    return None

def A_star(grid, START_POS, GOAL_POS):
    priority_queue = [
        Node(START_POS, parent=None, cost=0)
    ]
    path = []

    visited = set()
    while len(priority_queue) > 0:
        # Sort the queue, so that nodes which are closer heuristically are popped first
        # Total Cost for a node X = Heuristic Cost from X to Goal + Cost to reach X
        priority_queue.sort(key=lambda x: heuristic_function(x.pos, GOAL_POS) + x.cost, reverse=True)
        cur = priority_queue.pop()
        visited.add(cur.pos)
        if cur.pos == GOAL_POS:
            tmp = cur
            while tmp.parent is not None:
                path.append(tmp.pos)
                tmp = tmp.parent
            return path[1:], len(visited)
        neighbors = cur.get_neighbors(grid)

        for n in neighbors:
            if n not in visited:
                priority_queue.append(Node(n, parent=cur, cost=cur.cost + 1))
    return None


# DEFAULT
# def DFS(grid, START_POS, GOAL_POS):
#     stack = [
#         Node(START_POS, parent=None, cost=0)
#     ]
#     path = []

#     visited = set()
#     while len(stack) > 0:
#         stack = sorted(stack, key=lambda x: heuristic_function(x.pos, GOAL_POS) + x.cost)
#         cur = stack.pop()
#         visited.add(cur.pos)
#         if cur.pos == GOAL_POS:
#             tmp = cur
#             while tmp.parent is not None:
#                 path.append(tmp.pos)
#                 tmp = tmp.parent
#             print(f"visited_count: {len(visited)}")
#             return path[1:], len(visited)
#             return path[1:] # Excluding the goal pos
#         neighbors = cur.get_neighbors(grid)

#         # Select neighbor randomly (Random)
#         # random.shuffle(neighbors)

#         # Select neigbhor which is closer heuristically (Greedy Approach)
#         # neighbors.sort(key=lambda x: heuristic_function(x, GOAL_POS), reverse=True)

#         # Select neigbhor which is easier to reach and is closer heuristically (A* algorithm)
#         # neighbors.sort(key=lambda x: heuristic_function(x, GOAL_POS) + cur.cost, reverse=True)

#         for n in neighbors:
#             if n not in visited:
#                 stack.append(Node(n, parent=cur, cost=cur.cost + 1))
#     return None
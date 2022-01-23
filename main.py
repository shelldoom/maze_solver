import pygame
import sys
import random
from helper import A_star, DFS_greedy, DFS_random, draw_rect_with_border, load_grid, save_grid

pygame.init() # Do not move

FPS = 30
size = resX, resY = 800, 600
actual_size = resX, resY + 100
screen = pygame.display.set_mode(actual_size)
pygame.display.set_caption("test")
clock = pygame.time.Clock()

cell_w, cell_h = 50, 50
rows = resY//cell_w
cols = resX//cell_h

font = pygame.font.SysFont(None, 24)

# grid = [["EMPTY" for _ in range(cols)] for _ in range(rows)]
START_POS, GOAL_POS = None, None
LOAD_GRID_PATH = "./saves/default.txt"
grid, START_POS, GOAL_POS = load_grid(LOAD_GRID_PATH, (rows, cols))
PATH_LENGTH, VISITED_COUNT = None, None


DRAW_MODES = ["EMPTY", "WALL", "START", "GOAL"]
CUR_DRAW_MODE_INDEX = 1
CUR_DRAW_MODE = DRAW_MODES[CUR_DRAW_MODE_INDEX]

SEARCH_MODES = [
    ("DFS with random neighbor selection", DFS_random), 
    ("DFS with greedy neigbhor selection", DFS_greedy), 
    ("A* Algorithm", A_star)
]
CUR_SEARCH_MODE_INDEX = 0
CUR_SEARCH_MODE_FUNCTION = SEARCH_MODES[CUR_SEARCH_MODE_INDEX][1]

def draw_grid(grid):
    color_table = {
        "WALL": (80, 80, 80),
        "EMPTY": (237, 240, 252),
        "GOAL": (0, 171, 28),
        "START": (255, 0, 0),
        "PATH": (220, 235, 113)
    }

    x, y = 0, 0
    for i in range(rows):
        for j in range(cols):
            cell = pygame.Rect(x + cell_w*j, y + cell_h*i, cell_w, cell_h)
            cell_color = color_table.get(grid[i][j], color_table["EMPTY"])
            draw_rect_with_border(screen, cell_color, cell, 1, (0, 0, 0))

def remove_path(grid):
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == "PATH":
                grid[i][j] = "EMPTY"
    global PATH_LENGTH, VISITED_COUNT
    PATH_LENGTH, VISITED_COUNT = None, None

def clear_grid(grid):
    for i in range(rows):
        for j in range(cols):
            grid[i][j] = "EMPTY"
    global START_POS, GOAL_POS
    START_POS, GOAL_POS = None, None

while 1:
    pygame.display.flip()
    clock.tick(FPS)
    save_is_pressed = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                CUR_DRAW_MODE_INDEX += 1
                CUR_DRAW_MODE_INDEX %= len(DRAW_MODES)
                CUR_DRAW_MODE = DRAW_MODES[CUR_DRAW_MODE_INDEX]
            if event.key == pygame.K_m:
                CUR_SEARCH_MODE_INDEX += 1
                CUR_SEARCH_MODE_INDEX %= len(SEARCH_MODES)
                CUR_SEARCH_MODE_FUNCTION = SEARCH_MODES[CUR_SEARCH_MODE_INDEX][1]
                remove_path(grid)
            if event.key == pygame.K_RETURN:
                remove_path(grid)
                path, VISITED_COUNT = CUR_SEARCH_MODE_FUNCTION(grid, START_POS, GOAL_POS)
                PATH_LENGTH = len(path)
                for pos in path:
                    grid[pos[0]][pos[1]] = "PATH"
            if event.key == pygame.K_r:
                remove_path(grid)
            if event.key == pygame.K_c:
                clear_grid(grid)
    screen.fill(0)
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_LCTRL] and keys_pressed[pygame.K_s]:
        save_grid(grid)
    draw_grid(grid)

    # Bottom Info Text
    line1_y = resY + (actual_size[1] - size[1])//4
    DRAW_INFO = f"Draw Mode: {CUR_DRAW_MODE}" 
    SEARCH_INFO = f"Search Mode: {SEARCH_MODES[CUR_SEARCH_MODE_INDEX][0]}"
    screen.blit(font.render(DRAW_INFO, True, (200, 200, 200)), (50, line1_y))
    screen.blit(font.render(SEARCH_INFO, True, (200, 200, 200)), (250, line1_y))

    if PATH_LENGTH and VISITED_COUNT:
        line2_y = resY + 3*(actual_size[1] - size[1])//4
        COST_INFO = f"Path Length: {PATH_LENGTH}" 
        VISITED_INFO = f"No. of nodes visited: {VISITED_COUNT}"
        screen.blit(font.render(COST_INFO, True, (200, 200, 200)), (50, line2_y))
        screen.blit(font.render(VISITED_INFO, True, (200, 200, 200)), (250, line2_y))


    # Mouse Handling
    if pygame.mouse.get_pressed(3)[0]:
        mouseX, mouseY = pygame.mouse.get_pos()
        if mouseX > resX or mouseY > resY:
            continue
        click_i, click_j = mouseY//cell_h, mouseX//cell_w
        if CUR_DRAW_MODE == "START":
            if START_POS:
                grid[START_POS[0]][START_POS[1]] = "EMPTY"
            START_POS = click_i, click_j
            grid[click_i][click_j] = CUR_DRAW_MODE
        elif CUR_DRAW_MODE == "GOAL":
            if GOAL_POS:
                grid[GOAL_POS[0]][GOAL_POS[1]] = "EMPTY"
            GOAL_POS = click_i, click_j
            grid[click_i][click_j] = CUR_DRAW_MODE
        else:
            grid[click_i][click_j] = CUR_DRAW_MODE

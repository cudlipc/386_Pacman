import pygame
import random
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.image_fast = pygame.image.load('images/enemy_fast.bmp')
        self.image_fast2 = pygame.image.load('images/enemy_fast2.bmp')
        self.image_slow = pygame.image.load('images/enemy_slow.bmp')
        self.image_slow2= pygame.image.load('images/enemy_slow2.bmp')
        self.image_random = pygame.image.load('images/enemy_random.bmp')
        self.image_random2 = pygame.image.load('images/enemy_random2.bmp')
        self.image_scared = pygame.image.load('images/enemy_scared.bmp')
        self.image_scared2 = pygame.image.load('images/enemy_scared2.bmp')
        self.image_ghost = pygame.image.load('images/enemy_ghost.bmp')
        self.image_ghost2 = pygame.image.load('images/enemy_ghost2.bmp')
        self.image_eyes = pygame.image.load('images/enemy_eyes.bmp')
        self.expire_image = pygame.image.load('images/enemy_expire.bmp')
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.colour = self.set_colour()
        self.colour2 = self.set_colour2()
        self.saved_colour = self.set_colour()
        self.saved_colour2 = self.set_colour2()
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.ghost_state = False
        self.eye_state = False
        self.speed = self.set_speed()
        self.timer = pygame.time.get_ticks()

    def update(self):
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()
        if self.ghost_state:
            self.colour = self.image_ghost
            self.colour2 = self.image_ghost2
            if self.app.player.buff_timer <= (pygame.time.get_ticks()-8000):
                self.colour = self.expire_image
                self.colour2 = self.image_ghost
            if not self.app.player.gigabuff:
                self.colour = self.saved_colour
                self.colour2 = self.saved_colour2
        if self.eye_state:
            self.colour = self.image_eyes
            self.colour2 = self.image_eyes
            if not self.app.player.gigabuff:
                self.colour = self.saved_colour
                self.colour2 = self.saved_colour2

        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.app.cell_height//2)//self.app.cell_height+1

    def draw(self):
        if (pygame.time.get_ticks() - self.timer) % 400 >= 0 and (pygame.time.get_ticks() - self.timer) % 200 < 200:
            self.app.screen.blit(self.colour, (int(self.pix_pos.x) - self.app.cell_width/2, int(self.pix_pos.y) -self.app.cell_height/2))
        if (pygame.time.get_ticks() - self.timer) % 400 >= 200 and (pygame.time.get_ticks() - self.timer) % 200 < 400:
            self.app.screen.blit(self.colour2, (int(self.pix_pos.x) - self.app.cell_width / 2, int(self.pix_pos.y) - self.app.cell_height / 2))
        # pygame.draw.circle(self.app.screen, self.colour,
        #                   (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    def set_speed(self):
        if self.personality in ["speedy", "scared"]:
            speed = 2
        else:
            speed = 1
        return speed

    def set_target(self):
        if self.eye_state:
            if self.personality == "speedy":
                return self.app.ghost_start[0]
            if self.personality == "slow":
                return self.app.ghost_start[1]
            if self.personality == "random":
                return self.app.ghost_start[2]
            else:
                return self.app.ghost_start[3]
        elif self.personality == "speedy" or self.personality == "slow":
            return self.app.player.grid_pos
        else:
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)
            if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)
            else:
                return vec(COLS-2, ROWS-2)

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        if self.personality == "random":
            self.direction = self.get_random_direction()
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
                        int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    def get_pix_pos(self):
        return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2 +
                   self.app.cell_height//2)

    def set_colour(self):
        if self.number == 0:
            return self.image_fast
        if self.number == 1:
            return self.image_slow
        if self.number == 2:
            return self.image_random
        if self.number == 3:
            return self.image_scared

    def set_colour2(self):
        if self.number == 0:
            return self.image_fast2
        if self.number == 1:
            return self.image_slow2
        if self.number == 2:
            return self.image_random2
        if self.number == 3:
            return self.image_scared2

    def set_personality(self):
        if self.number == 0:
            return "speedy"
        elif self.number == 1:
            return "slow"
        elif self.number == 2:
            return "random"
        else:
            return "scared"

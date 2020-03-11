import pygame
from settings import *
vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app
        self.starting_pos = [pos.x, pos.y]
        self.image1 = pygame.image.load('images/pacman1.bmp')
        self.image2 = pygame.image.load('images/pacman2.bmp')
        self.image3 = pygame.image.load('images/pacman3.bmp')
        self.grid_pos = pos
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(1, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2
        self.lives = 3
        self.gigabuff = False
        self.timer = pygame.time.get_ticks()
        self.buff_timer = 0

    def update(self):
        if self.able_to_move:
            self.pix_pos += self.direction*self.speed
        if self.time_to_move():
            if self.stored_direction != None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()
        # Setting grid position in reference to pix pos
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.app.cell_height//2)//self.app.cell_height+1
        if self.on_coin():
            self.eat_coin()

        if self.on_gigacoin():
            self.eat_gigacoin()

        if self.on_portal():
            self.take_portal()

        if self.gigabuff:
            if self.buff_timer <= (pygame.time.get_ticks() - 10000):
                self.gigabuff = False

    def draw(self):
        if (pygame.time.get_ticks() - self.timer)%400 >= 0 and (pygame.time.get_ticks() - self.timer)%400 < 100:
            self.app.screen.blit(self.image1,(int(self.pix_pos.x-self.app.cell_width/2), int(self.pix_pos.y-self.app.cell_height/2)))
        elif (pygame.time.get_ticks() - self.timer) % 400 >= 100 and (pygame.time.get_ticks() - self.timer) % 400 < 200:
            self.app.screen.blit(self.image2, (int(self.pix_pos.x-self.app.cell_width / 2), int(self.pix_pos.y-self.app.cell_height / 2)))
        elif (pygame.time.get_ticks() - self.timer) % 400 >= 200 and (pygame.time.get_ticks() - self.timer) % 400 < 300:
            self.app.screen.blit(self.image3, (int(self.pix_pos.x-self.app.cell_width / 2), int(self.pix_pos.y-self.app.cell_height / 2)))
        elif (pygame.time.get_ticks() - self.timer) % 400 >= 300 and (pygame.time.get_ticks() - self.timer) % 400 < 400:
            self.app.screen.blit(self.image2, (int(self.pix_pos.x-self.app.cell_width / 2), int(self.pix_pos.y-self.app.cell_height / 2)))


        # pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (int(self.pix_pos.x),
        #                                                    int(self.pix_pos.y)), self.app.cell_width//2-2)

        # Drawing player lives
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (30 + 20*x, HEIGHT - 15), 7)

        # Drawing the grid pos rect
        # pygame.draw.rect(self.app.screen, RED, (self.grid_pos[0]*self.app.cell_width+TOP_BOTTOM_BUFFER//2,
        #                                         self.grid_pos[1]*self.app.cell_height+TOP_BOTTOM_BUFFER//2, self.app.cell_width, self.app.cell_height), 1)

    def on_coin(self):
        if self.grid_pos in self.app.coins:
            if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def on_gigacoin(self):
        if self.grid_pos in self.app.giga_coins:
            if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def on_portal(self):
        if self.grid_pos in self.app.portals:
            if int(self.pix_pos.x + TOP_BOTTOM_BUFFER // 2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y + TOP_BOTTOM_BUFFER // 2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def take_portal(self):
        self.app.portals.remove(self.grid_pos)
        self.grid_pos = self.app.portals[0]
        self.pix_pos = self.get_pix_pos()
        self.app.portals.remove(self.grid_pos)

    def eat_coin(self):
        self.app.coins.remove(self.grid_pos)
        self.current_score += 1

    def eat_gigacoin(self):
        self.app.giga_coins.remove(self.grid_pos)
        self.current_score += 1
        for enemy in self.app.enemies:
            enemy.ghost_state = True
        self.gigabuff = True
        self.buff_timer = pygame.time.get_ticks()

    def move(self, direction):
        self.stored_direction = direction

    def get_pix_pos(self):
        return vec((self.grid_pos[0]*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos[1]*self.app.cell_height) +
                   TOP_BOTTOM_BUFFER//2+self.app.cell_height//2)

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def can_move(self):
        for wall in self.app.walls:
            if vec(self.grid_pos+self.direction) == wall:
                return False
        return True

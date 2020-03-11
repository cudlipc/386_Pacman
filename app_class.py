import pygame
import sys
import copy
from settings import *
from player import *
from enemy import *


pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH//COLS
        self.cell_height = MAZE_HEIGHT//ROWS
        self.portal_img = pygame.image.load('images/portal.bmp')
        self.pacstart1 = pygame.image.load('images/pacmanstart1.bmp')
        self.pacstart2 = pygame.image.load('images/pacmanstart3.bmp')
        self.pacstart3 = pygame.image.load('images/pacmanstart3.bmp')
        self.redstart1 = pygame.image.load('images/redstart1.bmp')
        self.redstart2 = pygame.image.load('images/redstart2.bmp')
        self.bluestart1 = pygame.image.load('images/bluestart1.bmp')
        self.bluestart2 = pygame.image.load('images/bluestart2.bmp')
        self.orangestart1 = pygame.image.load('images/orangestart1.bmp')
        self.orangestart2 = pygame.image.load('images/orangestart2.bmp')
        self.pinkstart1 = pygame.image.load('images/pinkstart1.bmp')
        self.pinkstart2 = pygame.image.load('images/pinkstart2.bmp')
        self.walls = []
        self.coins = []
        self.giga_coins = []
        self.enemies = []
        self.portals = []
        self.valid_spawn = []
        self.bullet_direction = vec(1,0)
        self.e_pos = []
        self.ghost_start = []
        self.p_pos = None
        self.bullet_pos = vec(1,2)
        self.bullet_speed = 5
        self.bullet_pix_pos = self.get_bullet_pix_pos()
        self.load()
        self.portal_exist = False
        self.player = Player(self, vec(self.p_pos))
        self.start_pacman = vec(WIDTH, HEIGHT - HEIGHT//4)
        self.start_red = vec(WIDTH + 150, HEIGHT - HEIGHT//4)
        self.start_blue = vec(WIDTH + 250, HEIGHT - HEIGHT//4)
        self.start_orange = vec(WIDTH + 350, HEIGHT - HEIGHT//4)
        self.start_pink = vec(WIDTH + 450, HEIGHT - HEIGHT // 4)
        self.eat_counter = 1
        self.make_enemies()
        self.start_timer = pygame.time.get_ticks()
        self.game_timer = pygame.time.get_ticks()
        self.GAME_START, self.DEATH, self.CHOMP = 0,1,2
        sounds = [{self.GAME_START: 'sounds/pacman_beginning.wav',
                   self.DEATH: 'sounds/pacman_death.wav',
                   self.CHOMP: 'sounds/pacman_chomp.wav'}]
        self.audio = Audio(sounds=sounds, background_src=None, playing=True)

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def load(self):
        self.background = pygame.image.load('maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))

        # Opening walls file
        # Creating walls list with co-ords of walls
        # stored as  a vector
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(xidx, yidx))
                    elif char == "C":
                        self.coins.append(vec(xidx, yidx))
                        self.valid_spawn.append(vec(xidx, yidx))
                    elif char == "P":
                        self.p_pos = [xidx, yidx]
                    elif char in ["2", "3", "4", "5"]:
                        self.e_pos.append([xidx, yidx])
                        self.ghost_start.append([xidx, yidx])
                    elif char == "B":
                        pygame.draw.rect(self.background, BLACK, (xidx*self.cell_width, yidx*self.cell_height,
                                                                  self.cell_width, self.cell_height))
                    elif char == "K":
                        self.giga_coins.append(vec(xidx,yidx))

    def make_enemies(self):
        for idx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def draw_grid(self):
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.background, GREY, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.background, GREY, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))
        # for coin in self.coins:
        #     pygame.draw.rect(self.background, (167, 179, 34), (coin.x*self.cell_width,
        #                                                        coin.y*self.cell_height, self.cell_width, self.cell_height))

    def reset(self):
        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.coins = []
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(xidx, yidx))
                    if char == 'K':
                        self.giga_coins.append(vec(xidx, yidx))
        self.state = "playing"

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.audio.play_sound(sound=self.GAME_START)
                self.state = 'playing'

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PACMAN', self.screen, [WIDTH//2, HEIGHT//4], 64,(255,251,31), START_FONT, centered=True)
        self.draw_text('PUSH SPACE BAR', self.screen, [
                       WIDTH//2, HEIGHT//2-50], START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [
                       WIDTH//2, HEIGHT//2+50], START_TEXT_SIZE, (44, 167, 198), START_FONT, centered=True)
        self.draw_text('HIGH SCORE', self.screen, [4, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        if (pygame.time.get_ticks() - self.start_timer) % 400 >= 0 and (pygame.time.get_ticks() - self.start_timer) % 400 < 100:
            self.screen.blit(self.pacstart1, self.start_pacman)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 100 and (pygame.time.get_ticks() - self.start_timer) % 400 < 200:
            self.screen.blit(self.pacstart2, self.start_pacman)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 200 and (pygame.time.get_ticks() - self.start_timer) % 400 < 300:
            self.screen.blit(self.pacstart3, self.start_pacman)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 300 and (pygame.time.get_ticks() - self.start_timer) % 400 < 400:
            self.screen.blit(self.pacstart2, self.start_pacman)
        if (pygame.time.get_ticks() - self.start_timer) % 400 >= 0 and (pygame.time.get_ticks() - self.start_timer) % 400 < 200:
            self.screen.blit(self.redstart1, self.start_red)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 100 and (pygame.time.get_ticks() - self.start_timer) % 400 < 400:
            self.screen.blit(self.redstart2, self.start_red)
        if (pygame.time.get_ticks() - self.start_timer) % 400 >= 0 and (pygame.time.get_ticks() - self.start_timer) % 400 < 200:
            self.screen.blit(self.bluestart1, self.start_blue)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 100 and (pygame.time.get_ticks() - self.start_timer) % 400 < 400:
            self.screen.blit(self.bluestart2, self.start_blue)
        if (pygame.time.get_ticks() - self.start_timer) % 400 >= 0 and (pygame.time.get_ticks() - self.start_timer) % 400 < 200:
            self.screen.blit(self.orangestart1, self.start_orange)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 100 and (pygame.time.get_ticks() - self.start_timer) % 400 < 400:
            self.screen.blit(self.orangestart2, self.start_orange)
        if (pygame.time.get_ticks() - self.start_timer) % 400 >= 0 and (pygame.time.get_ticks() - self.start_timer) % 400 < 200:
            self.screen.blit(self.pinkstart1, self.start_pink)
        elif (pygame.time.get_ticks() - self.start_timer) % 400 >= 100 and (pygame.time.get_ticks() - self.start_timer) % 400 < 400:
            self.screen.blit(self.pinkstart2, self.start_pink)
        self.start_pacman[0] -= 1
        self.start_red[0] -= 1
        self.start_blue[0] -= 1
        self.start_orange[0] -= 1
        self.start_pink[0] -= 1
        if self.start_pacman[0] < -100:
            self.start_pacman[0] = WIDTH + 100
        if self.start_red[0] < -100:
            self.start_red[0] = WIDTH + 100
        if self.start_blue[0] < -100:
            self.start_blue[0] = WIDTH + 100
        if self.start_orange[0] < -100:
            self.start_orange[0] = WIDTH + 100
        if self.start_pink[0] < -100:
            self.start_pink[0] = WIDTH + 100
        pygame.display.update()

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))
                if event.key == pygame.K_SPACE and not self.portal_exist:
                    self.fire_portal()

    def playing_update(self):
        self.player.update()
        if self.game_timer - pygame.time.get_ticks()  < -550:
            self.audio.play_sound(sound=self.CHOMP)
            self.game_timer = pygame.time.get_ticks()
        if self.portal_exist:
            self.update_bullet()
            if self.bullet_pos in self.walls:
                self.create_portal(vec((self.bullet_pos[0]-self.bullet_direction.x),
                                   (self.bullet_pos[1]-self.bullet_direction.y)))
        for enemy in self.enemies:
            enemy.update()
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos and not self.player.gigabuff:
                self.audio.play_sound(sound=self.DEATH)
                self.remove_life()
            if enemy.grid_pos == self.player.grid_pos and self.player.gigabuff and not enemy.eye_state:
                enemy.ghost_state = False
                enemy.eye_state = True
                self.player.current_score += (200 * self.eat_counter)
                self.eat_counter += 1
        if not self.player.gigabuff:
            for enemy in self.enemies:
                enemy.ghost_state = False
                enemy.eye_state = False
                self.eat_counter = 1
        if self.coins.__len__() == 0 and self.giga_coins.__len__() == 0:
            self.reset()

    def playing_draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (TOP_BOTTOM_BUFFER//2, TOP_BOTTOM_BUFFER//2))
        self.draw_coins()
        # self.draw_grid()
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [60, 0], 18, WHITE, START_FONT)
        self.draw_text('HIGH SCORE: 0', self.screen, [WIDTH//2+60, 0], 18, WHITE, START_FONT)
        self.draw_portals()
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    def remove_life(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0
            while self.game_timer - pygame.time.get_ticks() < -1000:
                self.game_timer = self.game_timer

    def update_bullet(self):
        # print(self.bullet_pos)
        self.bullet_pix_pos += self.bullet_direction * self.bullet_speed
        self.bullet_pos[0] = (self.bullet_pix_pos[0] - TOP_BOTTOM_BUFFER +
                            self.cell_width // 2) // self.cell_width + 1
        self.bullet_pos[1] = (self.bullet_pix_pos[1] - TOP_BOTTOM_BUFFER +
                            self.cell_height // 2) // self.cell_height + 1

    def fire_portal(self):
        self.bullet_direction = copy.copy(self.player.direction)
        self.bullet_pix_pos = copy.copy(self.player.pix_pos)
        self.bullet_pos = copy.copy(self.player.grid_pos)
        self.portal_exist = True

    def get_bullet_pix_pos(self):
        return vec((self.bullet_pos[0]*self.cell_width)+TOP_BOTTOM_BUFFER//2+self.cell_width//2,
                   (self.bullet_pos[1]*self.cell_height) +
                   TOP_BOTTOM_BUFFER//2+self.cell_height//2)

    def create_portal(self, pos):
        if self.portals.__len__() != 0:
            self.portals = []
        out_port = vec(ROWS - pos.x, COLS - pos.y)
        counter = 0
        while out_port not in self.valid_spawn:
            if out_port.x >= 15 and counter == 0:
                out_port.x -= 1
            elif out_port.y >= 15 and counter == 1:
                out_port.y -= 1
            elif out_port.x < 15 and counter == 2:
                out_port.x += 1
            elif out_port.y < 15 and counter == 3:
                out_port.y += 1
            counter += 1
            if counter == 4:
                counter = 0

        if out_port in self.valid_spawn:
            self.portals.append(vec(pos.x, pos.y))
            self.portals.append(out_port)
        self.portal_exist = False

    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (124, 123, 7),
                               (int(coin.x*self.cell_width)+self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(coin.y*self.cell_height)+self.cell_height//2+TOP_BOTTOM_BUFFER//2), 5)
        for gigacoin in self.giga_coins:
            pygame.draw.circle(self.screen, (124, 123, 7),
                               (int(gigacoin.x * self.cell_width) + self.cell_width // 2 + TOP_BOTTOM_BUFFER // 2,
                                int(gigacoin.y * self.cell_height) + self.cell_height // 2 + TOP_BOTTOM_BUFFER // 2), 8)

    def draw_portals(self):
        for portal in self.portals:
            self.screen.blit(self.portal_img, (int((portal.x*self.cell_width)+self.cell_width//2+TOP_BOTTOM_BUFFER//2-self.cell_width//2),
                                int((portal.y*self.cell_height)+self.cell_height//2+TOP_BOTTOM_BUFFER//2-self.cell_height//2)))
            # pygame.draw.circle(self.screen, (224, 223, 7),
            #                  (int(portal.x*self.cell_width)+self.cell_width//2+TOP_BOTTOM_BUFFER//2,
            #                    int(portal.y*self.cell_height)+self.cell_height//2+TOP_BOTTOM_BUFFER//2), 5)

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [WIDTH//2, 100],  52, RED, "arial", centered=True)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  36, (190, 190, 190), "arial", centered=True)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  36, (190, 190, 190), "arial", centered=True)
        pygame.display.update()

class Audio:   # sound(s) and background music
    def __init__(self, sounds, background_src, playing):
        self.sounds = {}
        for sound in sounds:
            for k, v in sound.items():
                self.sounds[k] = pygame.mixer.Sound(v)
        self.background_src = background_src

        self.playing = playing
        if self.playing and self.background_src is not None:
            pygame.mixer.music.load(self.background_src)
        self.play_or_stop_background()

    def play_or_stop_background(self):
        if self.background_src is not None:
            pygame.mixer.music.play(-1, 0.0) if self.playing else pygame.mixer.music.stop()

    def play_sound(self, sound):
        if self.playing and sound in self.sounds.keys():
            self.sounds[sound].play()

    def toggle(self):
        self.playing = not self.playing
        self.play_or_stop_background()

    def game_over(self, game):
        pygame.playing = False
        self.play_or_stop_background()
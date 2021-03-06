import pygame
import sys
import os
import random
from collections import deque
from random import randint

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 480, 480
FPS = 25
MAPS_DIR = 'maps'
TILE_SIZE = 32
ENEMY_EVENT_TYPE = 30
INF = 700
keys_collected = 0
score = 0
screen_rect = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png", colorkey=-1)]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 5

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class Labyrinth:
    def __init__(self, filename, free_tiles, finish_tile, floor, wall):
        self.map = []
        with open(f"{MAPS_DIR}/{filename}") as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.floor = load_image(floor)
        self.wall = load_image(wall)
        self.tile_size = TILE_SIZE
        self.tile_size_x = WINDOW_WIDTH // self.width
        self.tile_size_y = WINDOW_HEIGHT // self.height
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile
        self.floor = pygame.transform.scale(self.floor, (self.tile_size_x, self.tile_size_y))
        self.wall = pygame.transform.scale(self.wall, (self.tile_size_x, self.tile_size_y))

    def load_map(self, filename,free_tiles, finish_tile):
        self.map = []
        with open(f"{MAPS_DIR}/{filename}") as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.tile_size_x = WINDOW_WIDTH // self.width
        self.tile_size_y = WINDOW_HEIGHT // self.height
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile
        self.floor = pygame.transform.scale(self.floor, (self.tile_size_x, self.tile_size_y))
        self.wall = pygame.transform.scale(self.wall, (self.tile_size_x, self.tile_size_y))

    def render(self, screen):
        colors = {0: self.floor, 1: self.wall, 2: self.floor}
        for y in range(self.height):
            for x in range(self.width):
                screen.blit(colors[self.get_tile_id((x, y))], (x * self.tile_size_x, y * self.tile_size_y))
                # rect = pygame.Rect(x * self.tile_size_x, y * self.tile_size_y,
                #                    self.tile_size_x, self.tile_size_y)
                # screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = deque()
        queue.append((x, y))
        while queue:
            x, y = queue.popleft()
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.height and \
                        self.is_free((next_x, next_y)) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(all_sprites)
        self.x, self.y = position
        self.image = load_image('mar.png')
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = position[0] * labyrinth.tile_size_x
        self.rect.y = position[1] * labyrinth.tile_size_y
        #all_sprites.remove(self)

    def resize(self):
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))
        self.mask = pygame.mask.from_surface(self.image)

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position
        self.rect.x = position[0] * labyrinth.tile_size_x
        self.rect.y = position[1] * labyrinth.tile_size_y

    def render(self, screen):
        screen.blit(self.image, (self.x * labyrinth.tile_size_x, self.y * labyrinth.tile_size_y))
        # center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        # pygame.draw.circle(screen, (255, 255, 255), center, TILE_SIZE // 2)


class Key(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(all_sprites)
        self.add(keys)
        self.image = load_image('key.jpg', colorkey=-1)
        #self.image = pygame.Surface((labyrinth.tile_size_x, labyrinth.tile_size_y),
        #                            pygame.SRCALPHA, 32)
        #image = load_image('key.jpg')
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))
        #pygame.draw.rect(self.image, pygame.Color("blue"), (0, 0, 20, 20), 0)
        #self.image.blit(image, (0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = position[0] * labyrinth.tile_size_x
        self.rect.y = position[1] * labyrinth.tile_size_y
        self.mask = pygame.mask.from_surface(self.image)


class Star(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(all_sprites)
        self.add(stars)
        self.image = load_image('star.jpg', colorkey=-1)
        # self.image = pygame.Surface((labyrinth.tile_size_x, labyrinth.tile_size_y),
        #                            pygame.SRCALPHA, 32)
        # image = load_image('key.jpg')
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))
        # pygame.draw.rect(self.image, pygame.Color("blue"), (0, 0, 20, 20), 0)
        # self.image.blit(image, (0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = position[0] * labyrinth.tile_size_x
        self.rect.y = position[1] * labyrinth.tile_size_y
        self.mask = pygame.mask.from_surface(self.image)


class Enemies:
    def __init__(self, position):
        self.x, self.y = position
        self.delay = INF
        self.image = load_image('bomb.png')
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def get_position(self):
        return self.x, self.y

    def resize(self):
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))

    def set_image(self):
        self.image = load_image('boom.png')
        self.image = pygame.transform.scale(self.image, (labyrinth.tile_size_x, labyrinth.tile_size_y))
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        screen.blit(self.image, (self.x * labyrinth.tile_size_x, self.y * labyrinth.tile_size_y))
        # center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        # pygame.draw.circle(screen, pygame.Color('brown'), center, TILE_SIZE // 2)


class Game:
    def __init__(self, labyrinth, player, enemy):
        self.labyrinth = labyrinth
        self.player = player
        self.enemy = enemy
        self.flag_enemy = False

    def render(self, screen):
        self.labyrinth.render(screen)
        self.player.render(screen)
        self.enemy.render(screen)

    def update_player(self):
        global keys_collected
        global score
        next_x, next_y = self.player.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.player.set_position((next_x, next_y))
            self.flag_enemy = True
        if pygame.sprite.spritecollide(self.player, keys, True):
            keys_collected += 1
        if pygame.sprite.spritecollide(self.player, stars, True):
            create_particles((self.player.get_position()[0] * self.labyrinth.tile_size_x, self.player.get_position()[1] * self.labyrinth.tile_size_y))
            score += 20

    def move_enemy(self):
        if self.flag_enemy:
            next_position = self.labyrinth.find_path_step(self.enemy.get_position(), self.player.get_position())
            self.enemy.set_position(next_position)

    def check_win(self):
        return self.labyrinth.get_tile_id(self.player.get_position()) == self.labyrinth.finish_tile and keys_collected == number_of_level

    def check_lose(self):
        return self.player.get_position() == self.enemy.get_position()

    def check_lvl(self, level):
        global keys_collected
        global sp
        file_name = 'field' + str(level) + '.txt'
        self.labyrinth.load_map(file_name, [0, 2], 2)
        self.player.set_position((self.labyrinth.width // 2, self.labyrinth.height // 2))
        self.enemy.set_position((7, 1))
        self.enemy.resize()
        self.player.resize()
        keys_collected = 0
        for x in sp:
            x.kill()
        sp = []
        for i in range(number_of_level):
            x = randint(1, 480 // labyrinth.tile_size_x - 1)
            y = randint(1, 480 // labyrinth.tile_size_y - 1)
            while not labyrinth.is_free((x, y)) or enemy.get_position() == (x, y):
                x = randint(1, 480 // labyrinth.tile_size_x - 1)
                y = randint(1, 480 // labyrinth.tile_size_y - 1)
            key = Key((x, y))
        for i in range(3):
            x = randint(1, 480 // labyrinth.tile_size_x - 1)
            y = randint(1, 480 // labyrinth.tile_size_y - 1)
            while not labyrinth.is_free((x, y)) or enemy.get_position() == (x, y):
                x = randint(1, 480 // labyrinth.tile_size_x - 1)
                y = randint(1, 480 // labyrinth.tile_size_y - 1)
            star = Star((x, y))
            sp.append(star)


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def show_score(screen, score):
    font = pygame.font.Font(None, 50)
    text = font.render('Счёт:' + str(score), True, (50, 70, 0))
    text_x = 0
    text_y = 0
    text_w = text.get_width()
    text_h = text.get_height()
    #pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


clock = pygame.time.Clock()
pygame.display.set_caption('Лабиринт')


def start_screen():
    intro_text = ["Лабиринт"]
    fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
running = True
game_over = False
number_of_level = 1
all_sprites = pygame.sprite.Group()
keys = pygame.sprite.Group()
stars = pygame.sprite.Group()
labyrinth = Labyrinth('field1.txt', [0, 2], 2, 'grass.png', 'box.png')
player = Player((7, 7))
enemy = Enemies((7, 1))
for i in range(number_of_level):
    x = randint(1, 480 // labyrinth.tile_size_x - 1)
    y = randint(1, 480 // labyrinth.tile_size_y - 1)
    while not labyrinth.is_free((x, y)) or enemy.get_position() == (x, y):
        x = randint(1, 480 // labyrinth.tile_size_x - 1)
        y = randint(1, 480 // labyrinth.tile_size_y - 1)
    key = Key((x, y))
sp = []
for i in range(3):
    x = randint(1, 480 // labyrinth.tile_size_x - 1)
    y = randint(1, 480 // labyrinth.tile_size_y - 1)
    while not labyrinth.is_free((x, y)) or enemy.get_position() == (x, y):
        x = randint(1, 480 // labyrinth.tile_size_x - 1)
        y = randint(1, 480 // labyrinth.tile_size_y - 1)
    star = Star((x, y))
    sp.append(star)
game = Game(labyrinth, player, enemy)
all_sprites.draw(screen)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == ENEMY_EVENT_TYPE and not game_over:
            game.move_enemy()
        if event.type == pygame.KEYDOWN and not game_over:
            game.update_player()
        screen.fill((0, 0, 0))
        labyrinth.render(screen)
        player.render(screen)
        game.render(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        show_score(screen, score)
        if game.check_lose():
            game_over = True
            enemy.set_image()
            enemy.render(screen)
            show_message(screen, 'You have lost!')
        if game.check_win() and number_of_level < 3:
            number_of_level += 1
            INF -= 100
            game.check_lvl(number_of_level)
        if game.check_win() and number_of_level == 3:
            game_over = True
            show_message(screen, 'You won!')
        pygame.display.flip()
        clock.tick(FPS)
pygame.quit()


def terminate():
    pygame.quit()
    sys.exit()



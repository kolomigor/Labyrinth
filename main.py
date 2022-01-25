import pygame
import sys
import os
import random
from collections import deque
from random import randint
import sqlite3

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 480, 480
FPS = 25
MAPS_DIR = 'maps'
TILE_SIZE = 32
ENEMY_EVENT_TYPE = 30
INF = 700
keys_collected = 0
screen_rect = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
playerName = ''


def terminate():
    pygame.quit()
    sys.exit()


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
        global sound_coin
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
            pygame.mixer.Sound("data/coin.mp3").play(loops=0)
        if pygame.sprite.spritecollide(self.player, stars, True):
            create_particles((self.player.get_position()[0] * self.labyrinth.tile_size_x, self.player.get_position()[1] * self.labyrinth.tile_size_y))
            pygame.mixer.Sound("data/coin.mp3").play(loops=0)
            score += 20

    def move_enemy(self):
        if self.flag_enemy:
            next_position = self.labyrinth.find_path_step(self.enemy.get_position(), self.player.get_position())
            self.enemy.set_position(next_position)

    def check_win(self):
        return self.labyrinth.get_tile_id(self.player.get_position()) == self.labyrinth.finish_tile and keys_collected == lvl

    def check_lose(self):
        return self.player.get_position() == self.enemy.get_position()

    def check_lvl(self, level):
        global keys_collected
        global sp
        file_name = 'field' + str(min(final_level, level)) + '.txt'
        self.labyrinth.load_map(file_name, [0, 2], 2)
        self.player.set_position((self.labyrinth.width // 2, self.labyrinth.height // 2))
        self.enemy.set_position((7, 1))
        self.enemy.resize()
        self.player.resize()
        keys_collected = 0
        for x in sp:
            x.kill()
        sp = []
        for i in range(lvl):
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


pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 26)


class InputBox:
    def __init__(self, x, y, w, h, text='', color='red'):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color(f'{color}')
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


def enter_screen():
    global playerName, can_main_game
    box1 = InputBox(20, 300, 200, 32)
    box = InputBox(20, 420, 120, 32, 'Войти')
    fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 20
    string_rendered = font.render("Вход в игру", True, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 10
    screen.blit(string_rendered, intro_rect)
    con = sqlite3.connect('data/base.db')
    cur = con.cursor()
    while True:
        pygame.display.set_caption('Вход')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            box1.handle_event(event)
            box.handle_event(event)
            if box.active:
                box.active = False
                name = box1.text
                result = cur.execute(f"""SELECT * FROM Players WHERE name='{name}'""").fetchall()
                if len(result) > 0:
                    playerName = name
                    can_main_game = True
                    return
                else:
                    cur.execute(f"""INSERT INTO Players(name, level, score) VALUES('{name}', 1, 0)""")
                    con.commit()
                    con.close()
                    playerName = name
                    can_main_game = True
                    pygame.display.flip()
                    return
        box.draw(screen)
        box1.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def rating_screen():
    intro_text = ["Рейтинг"]
    fon = pygame.transform.scale(load_image('rating_fon.jpg'), WINDOW_SIZE)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 20
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        screen.blit(string_rendered, intro_rect)
    con = sqlite3.connect('data/base.db')
    cur = con.cursor()
    cur_h = 50
    result = cur.execute("""SELECT * FROM Players""").fetchall()
    result.sort(key=lambda x: -x[2] * 1000 - x[3])
    boxes = [InputBox(10, cur_h, 110, 32, "Имя"), (InputBox(120, cur_h, 80, 32, "Уровень")),
             InputBox(200, cur_h, 60, 32, "Счет")]
    cur_h += 32
    for elem in result:
        boxes.append(InputBox(10, cur_h, 110, 32, str(elem[1])))
        boxes.append(InputBox(120, cur_h, 80, 32, str(elem[2])))
        boxes.append(InputBox(200, cur_h, 60, 32, str(elem[3])))
        cur_h += 32
    while True:
        pygame.display.set_caption('Рейтинг')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            for box in boxes:
                box.handle_event(event)
        for box in boxes:
            box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


can_main_game = False


def start_screen():
    pygame.mixer.music.load("data/start_screen_music.mp3")
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.3)
    input_box1 = InputBox(20, 420, 80, 32, 'Войти')
    input_box2 = InputBox(340, 20, 100, 32, 'Рейтинг')
    boxes = [input_box1, input_box2]
    fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 20
    string_rendered = font.render('Лабиринт', True, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 10
    screen.blit(string_rendered, intro_rect)
    while True:
        pygame.display.set_caption('Лабиринт')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            for box in boxes:
                box.handle_event(event)
            if input_box1.active and event.type == pygame.MOUSEBUTTONDOWN:
                pygame.display.flip()
                enter_screen()
                pygame.display.flip()
                fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
                screen.blit(fon, (0, 0))
                font = pygame.font.Font(None, 30)
                string_rendered = font.render('Лабиринт', True, pygame.Color('red'))
                intro_rect = string_rendered.get_rect()
                intro_rect.top = text_coord
                intro_rect.x = 10
                screen.blit(string_rendered, intro_rect)
                if can_main_game:
                    return
            if input_box2.active and event.type == pygame.MOUSEBUTTONDOWN:
                pygame.display.flip()
                rating_screen()
                pygame.display.flip()
                fon = pygame.transform.scale(load_image('fon.jpg'), WINDOW_SIZE)
                screen.blit(fon, (0, 0))
                font = pygame.font.Font(None, 30)
                string_rendered = font.render('Лабиринт', True, pygame.Color('red'))
                intro_rect = string_rendered.get_rect()
                intro_rect.top = text_coord
                intro_rect.x = 10
                screen.blit(string_rendered, intro_rect)
        for box in boxes:
            box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
pygame.mixer.music.stop()
con = sqlite3.connect('data/base.db')
cur = con.cursor()
pygame.display.set_caption('Лабиринт')
lst1 = cur.execute(f"""SELECT * FROM Players WHERE name='{playerName}'""").fetchall()
elem1 = lst1[0]
idPlayer = elem1[0]
score = elem1[3]
running = True
game_over = False
lvl = elem1[2]
all_sprites = pygame.sprite.Group()
keys = pygame.sprite.Group()
stars = pygame.sprite.Group()
final_level = 4
labyrinth = Labyrinth(f'field{min(final_level, lvl)}.txt', [0, 2], 2, 'grass.png', 'box.png')
player = Player((7, 7))
enemy = Enemies((7, 1))
for i in range(lvl):
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
first_lose = True
sound = pygame.mixer.Sound("data/game_music.mp3")
sound.set_volume(0.3)
sound.play()
already_won = False
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
            sound.stop()
            if first_lose:
                pygame.mixer.Sound("data/boom.mp3").play(loops=0)
            first_lose = False
            game_over = True
            enemy.set_image()
            enemy.render(screen)
            show_message(screen, 'You have lost!')
        if game.check_win():
            cur.execute(f"""UPDATE Players SET level={lvl + 1} WHERE id={idPlayer}""")
            cur.execute(f"""UPDATE Players SET score={score} WHERE id={idPlayer}""")
            con.commit()
        if game.check_win() and lvl < final_level:
            lvl += 1
            INF -= 100
            game.check_lvl(lvl)
        if game.check_win() and lvl >= final_level:
            game_over = True
            show_message(screen, 'You won!')
        pygame.display.flip()
        clock.tick(FPS)
pygame.quit()

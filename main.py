import pygame
import sys
import os

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 480, 480
FPS = 25
MAPS_DIR = 'maps'
TILE_SIZE = 32
ENEMY_EVENT_TYPE = 30


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


class Labyrint:
    def __init__(self, filename, free_tiles, finish_tile, floor, wall):
        self.map = []
        with open(f"{MAPS_DIR}/{filename}") as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.hight = len(self.map)
        self.width = len(self.map[0])
        self.floor = load_image(floor)
        self.wall = load_image(wall)
        self.tile_size = TILE_SIZE
        self.tile_size_x = WINDOW_WIDTH // self.width
        self.tile_size_y = WINDOW_HEIGHT // self.hight
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile
        self.floor = pygame.transform.scale(self.floor, (self.tile_size_x, self.tile_size_y))
        self.wall = pygame.transform.scale(self.wall, (self.tile_size_x, self.tile_size_y))

    def render(self, screen):
        colors = {0: self.floor, 1: self.wall, 2: self.floor}
        for y in range(self.hight):
            for x in range(self.width):
                screen.blit(colors[self.get_tile_id((x, y))], (x * self.tile_size_x, y * self.tile_size_y))
                #rect = pygame.Rect(x * self.tile_size_x, y * self.tile_size_y,
                #                   self.tile_size_x, self.tile_size_y)
                #screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def finde_path_step(self, start, target):
        INF = 1000
        x, y = start
        distance = [[INF] * self.width for _ in range(self.hight)]
        distance[x][y] = 0
        prev = [[None] * self.width for _ in range(self.hight)]
        que = [(x, y)]
        while que:
            x, y = que.pop(0)
            for dx, dy in (0, 1), (1, 0), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.hight and self.is_free((next_x, next_y)) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    que.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Player:
    def __init__(self, position):
        self.x, self.y = position
        self.image = load_image('mar.png')
        self.image = pygame.transform.scale(self.image, (labyrint.tile_size_x, labyrint.tile_size_y))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        screen.blit(self.image, (self.x * labyrint.tile_size_x, self.y * labyrint.tile_size_y))
        #center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        #pygame.draw.circle(screen, (255, 255, 255), center, TILE_SIZE // 2)


class Enemies:
    def __init__(self, position):
        self.x, self.y = position
        self.delay = 1000
        self.image = load_image('bomb.png')
        self.image = pygame.transform.scale(self.image, (labyrint.tile_size_x, labyrint.tile_size_y))
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        screen.blit(self.image, (self.x * labyrint.tile_size_x, self.y * labyrint.tile_size_y))
        #center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        #pygame.draw.circle(screen, pygame.Color('brown'), center, TILE_SIZE // 2)


class Game:
    def __init__(self, labyrint, player, enemy):
        self.labytint = labyrint
        self.player = player
        self.enemy = enemy
        self.flag_enemy = False

    def render(self, screen):
        self.labytint.render(screen)
        self.player.render(screen)
        self.enemy.render(screen)

    def update_player(self):
        next_x, next_y = self.player.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labytint.is_free((next_x, next_y)):
            self.player.set_position((next_x, next_y))
            self.flag_enemy = True

    def move_enemy(self):
        if self.flag_enemy:
            next_position = self.labytint.finde_path_step(self.enemy.get_position(), self.player.get_position())
            self.enemy.set_position(next_position)

    def check_win(self):
        return self.labytint.get_tile_id(self.player.get_position()) == self.labytint.finish_tile

    def check_lose(self):
        return self.player.get_position() == self.enemy.get_position()


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, 1, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
running = True
game_over = False
labyrint = Labyrint('field1.txt', [0, 2], 2, 'grass.png', 'box.png')
player = Player((7, 7))
enemy = Enemies((7, 1))
game = Game(labyrint, player, enemy)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == ENEMY_EVENT_TYPE and not game_over:
            game.move_enemy()
        if event.type == pygame.KEYDOWN and not game_over:
            game.update_player()
        screen.fill((0, 0, 0))
        labyrint.render(screen)
        player.render(screen)
        game.render(screen)
        if game.check_lose():
            game_over = True
            show_message(screen, 'You have lost!')
        if game.check_win():
            game_over = True
            show_message(screen, 'You won!')
        pygame.display.flip()
        clock.tick(FPS)
pygame.quit()
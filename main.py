import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 480, 480
FPS = 15
MAPS_DIR = 'maps'
TILE_SIZE = 32


class Labyrint:
    def __init__(self, filename, free_tiles, finish_tile):
        self.map = []
        with open(f"{MAPS_DIR}/{filename}") as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.hight = len(self.map)
        self.width = len(self.map[0])
        self.tile_size = TILE_SIZE
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile

    def render(self, screen):
        colors = {0: (0, 0, 0), 1:(120, 120, 120), 2: (50, 50, 50)}
        for y in range(self.hight):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                   self.tile_size, self.tile_size)
                screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles


class Player:
    def __init__(self, position):
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 255, 255), center, TILE_SIZE // 2)


class Game:
    def __init__(self, labyrint, player):
        self.labytint = labyrint
        self.player = player

    def render(self, screen):
        self.labytint.render(screen)
        self.player.render(screen)

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


pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
running = True
labyrint = Labyrint('field.txt', [0, 2], 2)
player = Player((7, 7))
game = Game(labyrint, player)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.update_player()
        screen.fill((0, 0, 0))
        labyrint.render(screen)
        player.render(screen)
        game.render(screen)
        pygame.display.flip()
        clock.tick(FPS)
pygame.quit()
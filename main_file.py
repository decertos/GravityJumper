from python_files.variables import *
from collections import deque
from random import choices
from PIL import Image
from time import time
import pygame
import os


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Generating frames
        self.frames = []
        for file_name in os.listdir("assets/frames"):
            if "lizard_m" in file_name:
                self.frames.append(pygame.image.load(f"assets/frames/{file_name}"))
                image_width, image_height = self.frames[-1].get_width(), self.frames[-1].get_height()
                self.frames[-1] = pygame.transform.scale(self.frames[-1],
                                                         (image_width * ENLARGING_COEFFICIENT,
                                                          image_height * ENLARGING_COEFFICIENT))
                self.frames[-1].set_colorkey((0, 0, 0))

        # Setting positions
        self.image = self.frames[0]
        self.current_image_index = 0
        self.rect = pygame.Rect(10, SCREEN_HEIGHT - self.image.get_height() - 5, self.image.get_width(), self.image.get_height())

        # Animation delay
        self.animation_delta = PLAYER_ANIMATION_DELTA
        self.prev_time = -1

    def change_image(self):
        if time() - self.prev_time < self.animation_delta:
            return
        # Setting new time
        self.prev_time = time()
        # Animation
        self.current_image_index = (self.current_image_index + 1) % len(self.frames)
        self.image = self.frames[self.current_image_index]
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def move(self, x, y):
        self.rect = self.rect.move(x, y)


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, images):
        super().__init__()
        self.images = images
        self.prev_time = -1
        self.animation_delta = TILE_ANIMATION_DELTA

        self.current_image_index = 0
        self.image = self.images[self.current_image_index]
        self.rect = pygame.Rect(position[0], position[1], self.image.get_width(), self.image.get_height())

    def change_image(self):
        if time() - self.prev_time < self.animation_delta:
            return
        self.prev_time = time()

        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image = self.images[self.current_image_index]
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class ElectricalTile(Tile):
    def __init__(self, position):
        images = []
        for file_name in os.listdir("assets/tiles_animations/electrical"):
            images.append(pygame.transform.scale(
                pygame.image.load(f"assets/tiles_animations/electrical/{file_name}"),
                (TILE_WIDTH * ENLARGING_COEFFICIENT, TILE_HEIGHT * ENLARGING_COEFFICIENT)))
            images[-1].set_colorkey((0, 0, 0))
        self.timer = 0
        super().__init__(position, images)

    def change_image(self):
        if time() - self.prev_time < self.animation_delta:
            return
        self.prev_time = time()
        self.timer += 1
        if self.timer >= 5:
            self.animation_delta = ACTIVATED_ELECTRICAL_TILE_ANIMATION_DELTA
        if self.timer >= 9:
            self.animation_delta = TILE_ANIMATION_DELTA
            self.timer = 1

        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image = self.images[self.current_image_index]
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def move(self, x, y):
        self.rect = self.rect.move(x, y)


def get_image(file, position, size, new_file_name):
    # Crop images
    tile_image = Image.open(file)
    x, y = position
    new_image = tile_image.crop(position + (position[0] + size[0], position[1] + size[1]))
    new_image.save(new_file_name)


def reload_images():
    # Wall images
    for i in range(WALL_IMAGES_COUNT):
        get_image("assets/images/all_walls.png", (i * WALL_WIDTH + i, 0), (WALL_WIDTH, WALL_HEIGHT), f"assets/images/wall_images/wall{i}.png")


if __name__ == "__main__":
    # Initializing the window
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = WALL_WIDTH * 3 * ENLARGING_COEFFICIENT, WALL_HEIGHT * ENLARGING_COEFFICIENT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Loading all images
    WALL_IMAGE_WIDTH, WALL_IMAGE_HEIGHT = 84 * ENLARGING_COEFFICIENT, 121 * ENLARGING_COEFFICIENT
    wall_images = []
    for image in os.listdir("assets/images/wall_images"):
        wall_images.append(pygame.transform.scale(pygame.image.load("assets/images/wall_images/" + image),
                                                  (WALL_IMAGE_WIDTH, WALL_IMAGE_HEIGHT)))

    # Adding sprites
    player_sprite = pygame.sprite.Group()
    player = Player()
    player_sprite.add(player)

    tiles = deque()

    ALL_TILES = [ElectricalTile]

    # Technical things
    clock = pygame.time.Clock()
    wall_render_delta = 0

    # Game loop
    running = True
    current_wall_images = deque(choices(wall_images, k=3) + choices(wall_images, k=3))
    for tile in [ElectricalTile(((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                                    SCREEN_HEIGHT - TILE_HEIGHT * 2))) for i in range(6)]:
        tiles.append(tile)

    while running:
        screen.fill("black")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        # Drawing
        for i in range(len(current_wall_images)):
            screen.blit(current_wall_images[i], (i * WALL_IMAGE_WIDTH - wall_render_delta, 0))

        player_sprite.draw(screen)

        for i in tiles:
            i.move(-WALLS_SPEED, 0)
            i.change_image()
            i.draw()

        # Walls rendering
        wall_render_delta += WALLS_SPEED
        if wall_render_delta >= WALL_IMAGE_WIDTH:
            current_wall_images.popleft()
            current_wall_images.append(choices(wall_images, k=1)[0])
            tiles.popleft()
            tiles.append(choices(ALL_TILES, k=1)[0]((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                                    SCREEN_HEIGHT - TILE_HEIGHT * 2)))
            wall_render_delta = 0

        # Animation
        player.change_image()

        # Display drawing
        clock.tick(FPS)
        pygame.display.flip()
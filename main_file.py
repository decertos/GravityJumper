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
        self.x, self.y = 10, SCREEN_HEIGHT - 70
        self.image = self.frames[0]
        self.current_image_index = 0
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        # Animation delay
        self.animation_delta = ANIMATION_DELTA
        self.prev_time = -1

    def change_image(self):
        if time() - self.prev_time < self.animation_delta:
            return
        # Setting new time
        self.prev_time = time()
        # Animation
        self.current_image_index = (self.current_image_index + 1) % len(self.frames)
        self.image = self.frames[self.current_image_index]
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


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

    # Technical things
    clock = pygame.time.Clock()
    wall_render_delta = 0

    # Game loop
    running = True
    current_wall_images = deque(choices(wall_images, k=3) + choices(wall_images, k=3))
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

        # Walls rendering
        wall_render_delta += WALLS_SPEED
        if wall_render_delta >= WALL_IMAGE_WIDTH:
            current_wall_images.popleft()
            current_wall_images.append(choices(wall_images, k=1)[0])
            wall_render_delta = 0

        # Animation
        player.change_image()

        # Display drawing
        clock.tick(FPS)
        pygame.display.flip()
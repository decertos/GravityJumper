from python_files.variables import *
from collections import deque
from random import choices, randint
from PIL import Image
from time import time
import pygame
import os


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Generating frames
        self.frames = []
        self.reversed_frames = []
        for file_name in os.listdir("assets/frames"):
            if "lizard_m" in file_name:
                self.frames.append(pygame.image.load(f"assets/frames/{file_name}"))
                self.reversed_frames.append(pygame.image.load(f"assets/frames/{file_name}"))

                image_width, image_height = self.frames[-1].get_width(), self.frames[-1].get_height()
                self.frames[-1] = pygame.transform.scale(self.frames[-1],
                                                         (image_width * ENLARGING_COEFFICIENT,
                                                          image_height * ENLARGING_COEFFICIENT))

                self.reversed_frames[-1] = pygame.transform.scale(self.reversed_frames[-1],
                                                                  (image_width * ENLARGING_COEFFICIENT,
                                                                   image_height * ENLARGING_COEFFICIENT))

                self.reversed_frames[-1] = pygame.transform.flip(self.reversed_frames[-1], False, True)
                self.frames[-1].set_colorkey((0, 0, 0))
                self.reversed_frames[-1].set_colorkey((0, 0, 0))

        # Setting positions
        self.image = self.frames[0]
        self.current_image_index = 0
        self.rect = pygame.Rect(20, SCREEN_HEIGHT - self.image.get_height() - 15, self.image.get_width(),
                                self.image.get_height())
        self.vx, self.vy = 0, 0
        self.up_pos = False

        # Animation delay
        self.animation_delta = PLAYER_ANIMATION_DELTA
        self.prev_time = -1

        self.collided = False
        self.flown = False

    def change_image(self):
        if time() - self.prev_time < self.animation_delta:
            return
        # Setting new time
        self.prev_time = time()
        # Animation
        self.current_image_index = (self.current_image_index + 1) % len(self.frames)
        if self.up_pos:
            self.image = self.reversed_frames[self.current_image_index]
        else:
            self.image = self.frames[self.current_image_index]
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def move(self):
        # Apply gravity based on current direction
        if self.up_pos:
            # Gravity is upwards, accelerate upwards (negative direction)
            self.vy -= 1
        else:
            # Gravity is downwards, accelerate downwards (positive direction)
            self.vy += 1

        # Check screen boundaries and stop if exceeded
        if self.vy != 0 and not self.flown:
            max_pos = TILE_HEIGHT * 3 if self.vy < 0 else SCREEN_HEIGHT - self.rect.height - 20
            if (self.vy > 0 and self.rect.y > max_pos) or (self.vy < 0 and self.rect.y < max_pos):
                self.rect.y = max_pos
                self.vy = 0

        # Move the player
        self.rect = self.rect.move(self.vx, self.vy)

        # Check if player has flown out of the screen
        if (self.rect.y > SCREEN_HEIGHT or self.rect.y < 0 - self.rect.height) and self.flown:
            exit(0)

    def tiles_check(self):
        collided = False
        # Check collision with ceiling tiles (tiles_up)
        for tile in tiles_up:
            if not tile.rect.colliderect(self.rect):
                continue
            collided = True
            # Handle special tiles
            if isinstance(tile, ElectricalTile):
                print(True, tile.timer)
                if tile.timer >= 5:
                    exit(0)
            elif isinstance(tile, BouncingTile):
                tile.bounced = True
                self.rect.y = tile.rect.bottom
                self.reverse_jump()
            else:
                # Regular ceiling tile: adjust position based on movement direction
                if self.vy < 0:  # Moving up into the tile
                    self.rect.top = tile.rect.bottom
                    self.vy = 0
                elif self.vy > 0:  # Moving down into the tile (unlikely but possible)
                    self.rect.bottom = tile.rect.top
                    self.vy = 0

        collided1 = False
        # Check collision with floor tiles (tiles_down)
        for tile in tiles_down:
            if not tile.rect.colliderect(self.rect):
                continue
            collided1 = True
            # Handle special tiles
            if isinstance(tile, ElectricalTile):
                if tile.timer >= 5:
                    exit(0)
            elif isinstance(tile, BouncingTile):
                tile.bounced = True
                self.rect.y = tile.rect.top - self.rect.height
                self.reverse_jump()
            else:
                # Regular floor tile: adjust position based on movement direction
                if self.vy > 0:  # Moving down into the tile
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vy < 0:  # Moving up into the tile
                    self.rect.top = tile.rect.bottom
                    self.vy = 0

        # Apply gravity if no collisions and not moving
        if self.vy == 0 and not collided and not collided1:
            self.vy = -5 if self.up_pos else 5
            self.flown = True

    def reverse_jump(self):
        if self.up_pos:
            self.image = self.frames[self.current_image_index]
            self.up_pos = not self.up_pos
            self.vy = 1
            return
        self.image = self.reversed_frames[self.current_image_index]
        self.up_pos = not self.up_pos
        self.vy = -1


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


class NormalTile(Tile):
    def __init__(self, position):
        frames = [pygame.transform.scale(pygame.image.load("assets/tiles_animations/normal/1.png"),
                                         (TILE_WIDTH * ENLARGING_COEFFICIENT,
                                          TILE_HEIGHT * ENLARGING_COEFFICIENT))]
        super().__init__(position, frames)


class BouncingTile(Tile):
    def __init__(self, position):
        frames = []
        for i in os.listdir("assets/tiles_animations/bouncing"):
            frames.append(pygame.transform.scale(pygame.image.load("assets/tiles_animations/bouncing/" + i),
                                                 (TILE_WIDTH * ENLARGING_COEFFICIENT,
                                                  TILE_HEIGHT * ENLARGING_COEFFICIENT)))
        super().__init__(position, frames)
        self.current_image_index = 0
        self.image = frames[0]
        self.bounced = False

    def change_image(self):
        if self.bounced:
            self.current_image_index += 1
            if self.current_image_index > 3:
                self.current_image_index = 0
                self.image = self.images[0]
                self.bounced = False
                return
            self.image = self.images[self.current_image_index]


def get_image(file, position, size, new_file_name):
    # Crop images
    tile_image = Image.open(file)
    x, y = position
    new_image = tile_image.crop(position + (position[0] + size[0], position[1] + size[1]))
    new_image.save(new_file_name)


def reload_images():
    # Wall images
    for i in range(WALL_IMAGES_COUNT):
        get_image("assets/images/all_walls.png", (i * WALL_WIDTH + i, 0), (WALL_WIDTH, WALL_HEIGHT),
                  f"assets/images/wall_images/wall{i}.png")


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

    tiles_up = deque()
    tiles_down = deque()

    ALL_TILES = [NormalTile, BouncingTile, ElectricalTile]

    # Technical things
    clock = pygame.time.Clock()
    wall_render_delta = 0
    score = 0

    # Game loop
    running = True
    current_wall_images = deque(choices(wall_images, k=4))
    for i, tile in enumerate([choices(ALL_TILES, k=1)[0] for i in range(4)]):
        new_tile = tile
        tiles_up.append(new_tile((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                  SCREEN_HEIGHT - TILE_HEIGHT * 2)))
        tiles_down.append(new_tile((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                    TILE_HEIGHT * 2)))

    while running:
        screen.fill("black")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.reverse_jump()

        # Drawing
        for i in range(len(current_wall_images)):
            screen.blit(current_wall_images[i], (i * WALL_IMAGE_WIDTH - wall_render_delta, 0))
        for i in tiles_up:
            i.rect.x -= WALLS_SPEED
            i.change_image()
            i.draw()
        for i in tiles_down:
            i.rect.x -= WALLS_SPEED
            i.change_image()
            i.draw()

        player_sprite.draw(screen)
        player.move()
        player.tiles_check()

        # Walls rendering
        wall_render_delta += WALLS_SPEED
        if wall_render_delta >= WALL_IMAGE_WIDTH:
            current_wall_images.popleft()
            current_wall_images.append(choices(wall_images, k=1)[0])
            tiles_up.popleft()
            tiles_down.popleft()
            up = choices(ALL_TILES, k=1)[0]((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                                        TILE_HEIGHT * 2))
            down = choices(ALL_TILES, k=1)[0]((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                                        SCREEN_HEIGHT - TILE_HEIGHT * 2))
            if isinstance(up, ElectricalTile) and isinstance(down, ElectricalTile):
                number = randint(1, 2)
                if number == 1:
                    up = NormalTile((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                                        TILE_HEIGHT * 2))
                elif number == 2:
                    down = NormalTile((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                                        SCREEN_HEIGHT - TILE_HEIGHT * 2))
            tiles_up.append(up)
            tiles_down.append(down)

            score += 1
            wall_render_delta = 0

        # Animation
        player.change_image()

        # Score
        font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 32)
        rendered = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(rendered, (SCREEN_WIDTH - rendered.get_width() - 5 * ENLARGING_COEFFICIENT,
                               rendered.get_height() - 5 * ENLARGING_COEFFICIENT))

        # Display drawing
        clock.tick(FPS)
        pygame.display.flip()

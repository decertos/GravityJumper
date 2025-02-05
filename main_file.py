from python_files.variables import *
from collections import deque
from random import choices, randint
from PIL import Image
from time import time
import pygame
import json
import math
import os

GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_SHOP = 2

game_state = GAME_STATE_MENU


def draw_main_menu():
    screen.fill("black")

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 64)
    title_text = font.render("Gravity Jumper", True, "white")
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    start_text = font.render("Play", True, "white")
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    shop_text = font.render("Shop", True, "white")
    shop_rect = shop_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

    quit_text = font.render("Quit", True, "white")
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4))

    screen.blit(title_text, title_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)

    if GAME_STATE_SHOP == 2:
        screen.blit(shop_text, shop_rect)

    return start_rect, quit_rect, shop_rect


def handle_menu_input(event, start_rect, quit_rect, shop_rect):
    global game_state

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = event.pos

        if start_rect.collidepoint(mouse_pos):
            game_state = GAME_STATE_PLAYING
            reset_game()
        elif quit_rect.collidepoint(mouse_pos):
            pygame.quit()
            exit()
        elif GAME_STATE_SHOP == 2 and shop_rect.collidepoint(mouse_pos):
            game_state = GAME_STATE_SHOP
            shop()


def reset_game():
    global coins, tiles_up, tiles_down, enemies, fireballs, player, coins_count, wall_render_delta, score, current_wall_images

    coins = []
    wall_render_delta = 0
    score = 0
    enemies = pygame.sprite.Group()
    fireballs = pygame.sprite.Group()

    player.rect = pygame.Rect(20, SCREEN_HEIGHT - player.image.get_height() - 15, player.image.get_width(),
                              player.image.get_height())
    player.vx, player.vy = 0, 0
    player.up_pos = False

    current_wall_images = deque(choices(wall_images, k=4))
    tiles_up = deque()
    tiles_down = deque()
    for i in range(4):
        up = choices(ALL_TILES, k=1)[0]((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                         TILE_HEIGHT * 2))
        down = choices(ALL_TILES, k=1)[0]((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                           SCREEN_HEIGHT - TILE_HEIGHT * 2))

        tiles_up.append(up)
        tiles_down.append(down)


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

        self.gravity_change_delta = 0.3
        self.prev_gravity_change = -1

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

        # Move the player
        self.rect = self.rect.move(self.vx, self.vy)

        # Check if player has flown out of the screen
        if self.rect.y > SCREEN_HEIGHT - 10 or self.rect.y < self.rect.height // 2 - TILE_HEIGHT * 2:
            save_data()
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
                if tile.timer >= 5:
                    save_data()
                    exit(0)
            elif isinstance(tile, BouncingTile):
                if self.flown:
                    continue
                tile.bounced = True
                self.rect.y = tile.rect.bottom
                self.reverse_jump()
                # Regular ceiling tile: adjust position based on movement direction
            if not isinstance(tile, BouncingTile):
                if self.vy > 0:  # Moving down into the tile
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vy < 0:  # Moving up into the tile
                    self.rect.top = tile.rect.bottom
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
                    save_data()
                    exit(0)
            elif isinstance(tile, BouncingTile):
                tile.bounced = True
                self.rect.y = tile.rect.top - self.rect.height
                self.reverse_jump()
                # Regular floor tile: adjust position based on movement direction
            if not isinstance(tile, BouncingTile):
                if self.vy > 0:  # Moving down into the tile
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vy < 0:  # Moving up into the tile
                    self.rect.top = tile.rect.bottom
                    self.vy = 0

        # Apply gravity if no collisions and not moving
        if self.vy == 0 and not collided and not collided1:
            self.vy = -5 if self.up_pos else 5

    def coins_check(self):
        global coins_count

        to_pop = []
        for i in range(len(coins)):
            if self.rect.colliderect(coins[i].rect):
                to_pop.append(i)
                coins_count += 1
        delta = 0
        for i in to_pop:
            coins.pop(i - delta)
            delta += 1

    def fireballs_check(self):
        global fireballs

        for i in fireballs:
            if i.rect.colliderect(self.rect):
                save_data()
                exit(0)

    def enemies_check(self):
        global enemies

        for i in enemies:
            if isinstance(i, KillingEnemy):
                if i.collision_rect.colliderect(self.rect):
                    save_data()
                    exit(0)

    def reverse_jump(self):
        if time() - self.prev_gravity_change < self.gravity_change_delta:
            return
        self.prev_gravity_change = time()
        if self.up_pos:
            self.image = self.frames[self.current_image_index]
            self.up_pos = not self.up_pos
            self.vy = 1
            return
        self.image = self.reversed_frames[self.current_image_index]
        self.up_pos = not self.up_pos
        self.vy = -1

    def draw_a_hitbox(self):
        pygame.draw.rect(screen, pygame.Color("green"), self.rect, width=1)


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

    def draw_a_hitbox(self):
        pygame.draw.rect(screen, pygame.Color("blue"), self.rect, width=1)


class ElectricalTile(Tile):
    frames = []
    for file_name in os.listdir("assets/tiles_animations/electrical"):
        frames.append(pygame.transform.scale(
            pygame.image.load(f"assets/tiles_animations/electrical/{file_name}"),
            (TILE_WIDTH * ENLARGING_COEFFICIENT, TILE_HEIGHT * ENLARGING_COEFFICIENT)))
        frames[-1].set_colorkey((0, 0, 0))

    def __init__(self, position):
        images = ElectricalTile.frames
        self.timer = randint(0, 4)
        super().__init__(position, images)
        self.image = images[self.timer]
        self.current_image_index = self.timer

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
    frames = [pygame.transform.scale(pygame.image.load("assets/tiles_animations/normal/1.png"),
                                     (TILE_WIDTH * ENLARGING_COEFFICIENT,
                                      TILE_HEIGHT * ENLARGING_COEFFICIENT))]

    def __init__(self, position):
        frames = NormalTile.frames
        super().__init__(position, frames)


class BouncingTile(Tile):
    frames = []
    for i in os.listdir("assets/tiles_animations/bouncing"):
        frames.append(pygame.transform.scale(pygame.image.load("assets/tiles_animations/bouncing/" + i),
                                             (TILE_WIDTH * ENLARGING_COEFFICIENT,
                                              TILE_HEIGHT * ENLARGING_COEFFICIENT)))

    def __init__(self, position):
        frames = BouncingTile.frames
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


class Coin(pygame.sprite.Sprite):
    images = []
    for i in os.listdir("assets/frames"):
        image = pygame.image.load("assets/frames/" + i)
        if "coin_anim_f" in i:
            images.append(pygame.transform.scale(image, (ENLARGING_COEFFICIENT * image.get_width(),
                                                         ENLARGING_COEFFICIENT * image.get_height())))

    def __init__(self, x, y):
        super().__init__()
        self.images = Coin.images
        self.image = self.images[0]
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.current_image_index = 0
        self.animation_delta = 0.1
        self.prev_animation = -1

        self.delta = 1

    def change_image(self):
        if time() - self.prev_animation < self.animation_delta:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image = self.images[self.current_image_index]
        self.prev_animation = time()

        self.delta = -self.delta

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y + self.delta))

    def draw_a_hitbox(self):
        pygame.draw.rect(screen, pygame.Color("yellow"), self.rect, width=1)


class FireEnemy(pygame.sprite.Sprite):
    images = []
    reversed_images = []
    for i in os.listdir("assets/frames"):
        if "chort_idle_anim" in i:
            image = pygame.image.load("assets/frames/" + i)
            image1 = pygame.transform.flip(image, True, False)
            images.append(pygame.transform.scale(image1, (image.get_width() * ENLARGING_COEFFICIENT,
                                                          image.get_height() * ENLARGING_COEFFICIENT)))
            image2 = pygame.transform.flip(image, True, True)
            reversed_images.append(pygame.transform.scale(image2, (image.get_width() * ENLARGING_COEFFICIENT,
                                                                   image.get_height() * ENLARGING_COEFFICIENT)))

    def __init__(self, position, reversed_image):
        super().__init__()

        self.images = FireEnemy.images if not reversed_image else FireEnemy.reversed_images
        self.current_index = 0
        self.image = self.images[self.current_index]
        self.animation_change_rate = 0.1
        self.prev_animation_change = -1
        self.rect = pygame.Rect(position[0], position[1], self.image.get_width(), self.image.get_height())

    def change_animation(self):
        if time() - self.prev_animation_change < self.animation_change_rate:
            return
        self.prev_animation_change = time()
        self.current_index = (self.current_index + 1) % len(self.images)
        self.image = self.images[self.current_index]

    def move(self, x, y):
        self.rect = self.rect.move(x, y)

    def draw_a_hitbox(self):
        pygame.draw.rect(screen, pygame.Color("red"), self.rect, width=1)


class FireBall(pygame.sprite.Sprite):
    images = []
    for i in os.listdir("assets/fireball"):
        image = pygame.image.load("assets/fireball/" + i)
        image = pygame.transform.flip(image, True, False)
        images.append(pygame.transform.scale(image, (image.get_width(),
                                                     image.get_height())))

    def __init__(self, position, velocity):
        super().__init__()
        self.images = []
        for i in FireBall.images:
            new_image = pygame.transform.rotate(i, 360 - math.degrees(math.atan(velocity[1] / velocity[0])))
            self.images.append(new_image)
        self.current_image = 0
        self.image = self.images[self.current_image]
        bounding_rect = self.image.get_bounding_rect()
        self.rect = bounding_rect.copy()
        self.rect.center = position
        self.vx, self.vy = velocity

        self.animation_delay = 0.1
        self.prev_animation_time = -1

    def change_animation(self):
        if time() - self.prev_animation_time < self.animation_delay:
            return
        self.prev_animation_time = time()
        self.current_image = (self.current_image + 1) % len(self.images)
        self.image = self.images[self.current_image]

    def move(self):
        self.rect = self.rect.move(self.vx, self.vy)

    def draw_a_hitbox(self):
        pygame.draw.rect(screen, pygame.Color("orange"), self.rect, width=1)


class KillingEnemy(pygame.sprite.Sprite):
    images = []
    reversed_images = []
    run_images = []
    reversed_run_images = []
    for i in os.listdir("assets/frames"):
        if "big_demon_idle_anim_f" in i:
            image = pygame.image.load("assets/frames/" + i)
            image = pygame.transform.scale(image, (image.get_width() * 1.5,
                                                   image.get_height() * 1.5))
            images.append(image)
            reversed_images.append(pygame.transform.flip(image, False, True))
        elif "big_demon_run_anim_f" in i:
            image = pygame.image.load("assets/frames/" + i)
            image = pygame.transform.scale(image, (image.get_width() * 1.5,
                                                   image.get_height() * 1.5))
            run_images.append(image)
            reversed_run_images.append(pygame.transform.flip(image, False, True))

    def __init__(self, position, rotation):
        super().__init__()
        if not rotation:
            self.images = KillingEnemy.images
            self.run_images = KillingEnemy.run_images
        else:
            self.images = KillingEnemy.reversed_images
            self.run_images = KillingEnemy.reversed_run_images
        self.current_index = 0
        self.image = self.images[self.current_index]
        self.rect = pygame.Rect(position[0], position[1], self.image.get_width(), self.image.get_height())
        self.collision_rect = self.image.get_bounding_rect()
        self.collision_rect.center = self.rect.center

        self.animation_delta = 0.1
        self.prev_animation_time = -1
        self.running = False

        self.rotation = rotation

    def change_animation(self):
        if time() - self.prev_animation_time < self.animation_delta:
            return
        self.prev_animation_time = time()
        self.current_index = (self.current_index + 1) % len(self.images)
        if self.running:
            self.image = self.run_images[self.current_index]
        else:
            self.image = self.images[self.current_index]

    def follow_player(self):
        self.rect = self.rect.move(-WALLS_SPEED, 0)
        self.collision_rect = self.collision_rect.move(-WALLS_SPEED, 0)
        return
        if self.rect.x == player.rect.x:
            self.running = False
            return
        vx = (player.rect.x - self.rect.x) // abs(player.rect.x - self.rect.x) * 3
        collided = False
        if self.rotation:
            for i in tiles_up:
                if self.rect.move(vx, -1).colliderect(i):
                    collided = True
                    break
        else:
            for i in tiles_down:
                if self.rect.move(vx, 2).colliderect(i):
                    collided = True
                    return
        if collided:
            self.running = True
            self.rect = self.rect.move(vx, 0)
            self.collision_rect = self.collision_rect.move(vx, 0)
            if vx < 0:
                self.image = pygame.transform.flip(self.images[self.current_index], True, False)
        else:
            self.running = False

    def draw_a_hitbox(self):
        pygame.draw.rect(screen, pygame.Color("red"), self.collision_rect, width=1)


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


def save_data():
    with open("game_save.json", "w") as f:
        json.dump({"coins": coins_count, "high_score": max(score, high_score)}, f)


def shop():
    running = True
    buttons = []
    while running:
        screen.fill("black")

        pygame.display.update()


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
    coins = []
    coins_count = 0
    high_score = 0
    prev_show_coin_frame_time = -1
    current_show_coin_frame = -1
    show_coin_frames = Coin.images

    try:
        with open("game_save.json") as f:
            all_data = json.load(f)
            coins_count += all_data["coins"]
            high_score = all_data["high_score"]
            print(coins_count)
    except Exception as e:
        print("Не найден файл сохранения. Возможно, он был перенесён.")

    ALL_TILES = [NormalTile, BouncingTile, ElectricalTile]

    # Technical things
    clock = pygame.time.Clock()
    wall_render_delta = 0
    score = 0
    is_bossfight = False
    bossfight_time = -1

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if game_state == GAME_STATE_MENU:
                start_rect, quit_rect, shop_rect = draw_main_menu()
                handle_menu_input(event, start_rect, quit_rect, shop_rect)
            elif game_state == GAME_STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.reverse_jump()

        if game_state == GAME_STATE_PLAYING:
            screen.fill("black")
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
            player.coins_check()

            # Walls rendering
            wall_render_delta += WALLS_SPEED
            if wall_render_delta >= WALL_IMAGE_WIDTH:
                current_wall_images.popleft()
                current_wall_images.append(choices(wall_images, k=1)[0])
                tiles_up.popleft()
                tiles_down.popleft()
                if not is_bossfight:
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
                    score += 1
                else:
                    up = NormalTile((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                     TILE_HEIGHT * 2))
                    down = NormalTile((3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH,
                                       SCREEN_HEIGHT - TILE_HEIGHT * 2))
                    if randint(1, 100) >= 40:
                        if randint(1, 2) == 1:
                            x = randint(
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - FireEnemy.images[0].get_width(),
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 + FireEnemy.images[0].get_width())
                            enemies.add(FireEnemy((x, tiles_up[0].rect.bottom), True))
                        else:
                            x = randint(
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - FireEnemy.images[0].get_width(),
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 + FireEnemy.images[0].get_width())
                            enemies.add(FireEnemy((x, tiles_down[0].rect.top - FireEnemy.images[0].get_height()),
                                                  False))
                    else:
                        if randint(1, 2) == 1:
                            x = randint(
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - KillingEnemy.images[0].get_width(),
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 + KillingEnemy.images[0].get_width())
                            enemies.add(KillingEnemy((x, tiles_up[0].rect.bottom), True))
                        else:
                            x = randint(
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - KillingEnemy.images[0].get_width(),
                                3 * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 + KillingEnemy.images[0].get_width())
                            enemies.add(
                                KillingEnemy((x, tiles_down[0].rect.top - KillingEnemy.images[0].get_height()),
                                             False))
                        print("a")

                    if randint(1, 1) == 1:
                        if 2 < len(enemies.sprites()):
                            rnd = randint(2, len(enemies.sprites()))

                            pos = 1
                            for i in enemies:
                                if rnd == pos and isinstance(i, FireEnemy):
                                    dx, dy = player.rect.x - i.rect.x, player.rect.y - i.rect.y
                                    if dx != 0 and dy != 0:
                                        if randint(1, 2) == 1:
                                            fireballs.add(
                                                FireBall((i.rect.x, i.rect.y),
                                                         (randint(-10, -1), dy // abs(dy) * 5)))
                                        else:
                                            fireballs.add(FireBall((i.rect.x, i.rect.y), (-10, 0)))
                                pos += 1

                tiles_up.append(up)
                tiles_down.append(down)

                wall_render_delta = 0

            if score % 10 == 0 and score != 0 and not is_bossfight:
                is_bossfight = True
                bossfight_time = time()
                player.gravity_change_delta = 0.2

            if is_bossfight and time() - bossfight_time > BOSSFIGHT_TIME:
                is_bossfight = False
                player.gravity_change_delta = 0.3
                score += 1

            to_pop = []
            for i in enemies:
                if isinstance(i, FireEnemy):
                    i.move(-WALLS_SPEED, 0)
                elif isinstance(i, KillingEnemy):
                    i.follow_player()
                i.change_animation()
                if i.rect.x + i.rect.width < 0:
                    to_pop.append(i)

            delta = 0
            for i in to_pop:
                enemies.remove(i)
                delta += 1
            enemies.draw(screen)

            player.enemies_check()

            to_pop = []
            for i in fireballs:
                i.move()
                i.change_animation()
                if i.rect.x + i.rect.width < 0:
                    to_pop.append(i)

            delta = 0
            for i in to_pop:
                fireballs.remove(i)
                delta += 1

            fireballs.draw(screen)
            player.fireballs_check()

            to_pop = []
            for coin in coins:
                if coin.rect.x < 0:
                    to_pop.append(coin)

            for to_pop in []:
                coins.remove(to_pop)

            for coin in coins:
                coin.rect.x -= WALLS_SPEED
                coin.change_image()
                coin.draw()

            if len(coins) < COINS_VISIBILITY_LIMIT and randint(1,
                                                               COINS_APPEND_CHANCE) == COINS_APPEND_CHANCE and not is_bossfight:
                coins.append(Coin(randint(SCREEN_WIDTH, 2 * SCREEN_WIDTH),
                                  randint(tiles_up[0].rect.bottom, tiles_down[0].rect.top - 1)))

            # Animation
            player.change_image()

            # Score
            font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 32)
            rendered = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(rendered, (SCREEN_WIDTH - rendered.get_width() - 5 * ENLARGING_COEFFICIENT,
                                   rendered.get_height() - 5 * ENLARGING_COEFFICIENT))

            if time() - prev_show_coin_frame_time > COIN_ANIMATION_DELTA:
                current_show_coin_frame = (current_show_coin_frame + 1) % len(show_coin_frames)
                prev_show_coin_frame_time = time()

            rendered1 = font.render(str(coins_count), True, (255, 255, 255))
            screen.blit(show_coin_frames[current_show_coin_frame],
                        (SCREEN_WIDTH - rendered1.get_width() - ENLARGING_COEFFICIENT * 20,
                         rendered.get_height() + 12 * ENLARGING_COEFFICIENT))
            screen.blit(rendered1, (SCREEN_WIDTH - rendered1.get_width() - 5 * ENLARGING_COEFFICIENT,
                                    rendered.get_height() + 10 * ENLARGING_COEFFICIENT))

            if DRAW_HITBOXES:
                player.draw_a_hitbox()
                for i in tiles_up:
                    i.draw_a_hitbox()
                for i in tiles_down:
                    i.draw_a_hitbox()
                for i in enemies:
                    i.draw_a_hitbox()
                for i in coins:
                    i.draw_a_hitbox()
                for i in fireballs:
                    i.draw_a_hitbox()

        elif game_state == GAME_STATE_SHOP:
            shop()
            game_state = GAME_STATE_MENU

        elif game_state == GAME_STATE_MENU:
            start_rect, quit_rect, shop_rect = draw_main_menu()
            handle_menu_input(event, start_rect, quit_rect, shop_rect)

        # Display drawing
        clock.tick(FPS)
        pygame.display.flip()

    save_data()

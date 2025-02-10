from python_files.variables import *
from python_files.upgrades import *
from collections import deque
from random import choices, randint
from PIL import Image
from time import time
import pygame
import json
import math
import os


def get_images(contains=""):
    # A function to get sprite images
    images = []
    for i in os.listdir("assets/frames"):
        if contains in i:
            image = pygame.image.load("assets/frames/" + i)
            images.append(image)
    return images


pygame.mixer.init(44100, 16, 2, 4096)
sound_on = True
pygame.mixer.music.load("sounds/background_music.mp3")

if sound_on:
    pygame.mixer.music.stop()
    pygame.mixer.music.load("sounds/background_music.mp3")
    pygame.mixer.music.play(-1, 0.0)


sound_effects = {"run": pygame.mixer.Sound("sounds/run.mp3"),
                 "jump": pygame.mixer.Sound("sounds/jump.mp3"),
                 "buy": pygame.mixer.Sound("sounds/buy.mp3"),
                 "buy_max": pygame.mixer.Sound("sounds/buy_max.mp3"),
                 "button_click": pygame.mixer.Sound("sounds/button_click.mp3"),
                 "background_music": pygame.mixer.Sound("sounds/background_music.mp3"),
                 "death_sound": pygame.mixer.Sound("sounds/death_sound.mp3"),
                 "revival": pygame.mixer.Sound("sounds/revival.mp3"),
                 "coin_collected": pygame.mixer.Sound("sounds/coin_collected.mp3"),
                 "bounce": pygame.mixer.Sound("sounds/bounce.mp3"),
                 "electrical_tile": pygame.mixer.Sound("sounds/electrical_tile.mp3")
                 }


# Reloading save files is they are deleted
characters_list = ["Lizard", "Female Lizard", "Dwarf", "Knight", "Female Knight", "Skeleton", "Elf", "Pumpkin Dude",
                   "Doctor"]
if not os.path.isfile("saves/obtained.json"):
    with open("saves/obtained.json", "w", encoding="UTF-8") as f:
        dictionary = {i: False for i in characters_list}
        dictionary["Lizard"] = True
        json.dump(dictionary, f)
if not os.path.isfile("saves/game_save.json"):
    with open("saves/game_save.json", "w", encoding="UTF-8") as f:
        json.dump({"coins": 0, "high_score": 0, "selected": "Lizard"}, f)
if not os.path.isfile("saves/shop_save.json"):
    with open("saves/shop_save.json", "w", encoding="UTF-8") as f:
        json.dump({"heart_up": False, "money_chance_up": 0, "boss_time_up": 0, "money_mult_up": False}, f)
if not os.path.isfile("saves/characters.json"):
    with open("saves/characters.json", "w", encoding="UTF-8") as f:
        json.dump({"Lizard": ["Just a normal lizard.\nIt is the first character\nthat you have!", 0],
                   "Doctor": ["Who knows what he carries\nwith himself?\nMaybe it's something\ndangerous!", 120],
                   "Skeleton": ["Is it cute or scary?\nSpooky scary skeletons...", 70],
                   "Dwarf": ["A cute dwarf. It will\nnot harm you. Buy it!", 50],
                   "Elf": ["It is a kind girl\nShe's an elf.\nShe likes music and dancing.", 90],
                   "Pumpkin Dude": ["I think you don't want\nto meet him at night...", 100],
                   "Female Lizard": ["It's a lizard like\nthe one you have, but\nit's recoloured!", 50],
                   "Knight": ["A brave knight! He can\nhelp you to jump... Maybe,\nyou won't spot the difference.", 60],
                   "Female Knight": ["She's as brave as another\nversion. But she has a red tail.", 60]}, f)

# Game state set
game_state = GAME_STATE_MENU
# Setting characters
characters = json.load(open("saves/characters.json"))
obtained_characters = json.load(open("saves/obtained.json"))
all_images = {"Lizard": get_images("lizard_m_run"), "Female Lizard": get_images("lizard_f_run"),
              "Dwarf": get_images("dwarf_f_run"), "Knight": get_images("knight_m_run"),
              "Female Knight": get_images("knight_f_run"), "Skeleton": get_images("skelet_run"),
              "Elf": get_images("elf_f_run"), "Pumpkin Dude": get_images("pumpkin_dude_run"),
              "Doctor": get_images("doc_run_anim")}

# Death animation frames
death_frames = []
for i in os.listdir("assets/death_explosion"):
    image = pygame.image.load("assets/death_explosion/" + i)
    death_frames.append(pygame.transform.scale(image, (image.get_width() * ENLARGING_COEFFICIENT,
                                                       image.get_height() * ENLARGING_COEFFICIENT)))


def draw_skins_avatar(image, title, description, price, bought=True):
    # A tab for a skin shop
    screen.fill("black")

    background_image = pygame.image.load("assets/images/main_menu.png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background_image, (0, 0))

    exit_button_image = pygame.image.load("assets/buttons/exit_button.png")
    exit_button_image = pygame.transform.scale(exit_button_image, (32, 32))
    screen.blit(exit_button_image, (10, 10))

    screen.blit(image, (40, SCREEN_HEIGHT // 2 - image.get_height() // 2))

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 42)
    title_text = font.render(title, True, "white")
    screen.blit(title_text, (
    40 + image.get_width() + 40 + (SCREEN_WIDTH - (40 + image.get_width() + 40)) // 2 - title_text.get_width() // 2,
    40))

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 28)
    text_line_height = None
    for i, text_data in enumerate(description.split("\n")):
        row_text = font.render(text_data, True, "gray")
        screen.blit(row_text,
                    (40 + image.get_width() + 40, 40 + title_text.get_height() + 20 + i * (row_text.get_height() + 1)))
        text_line_height = 40 + title_text.get_height() + 20 + i * (row_text.get_height() + 1)

    price_text = font.render("Price: ", True, "orange")
    screen.blit(price_text, (40 + image.get_width() + 40, text_line_height + 40))

    coins_icon = Coin.images[0]
    screen.blit(coins_icon, (40 + image.get_width() + 40 + price_text.get_width() + 10, text_line_height + 40))
    coins_text = font.render(str(price), True, "white")
    screen.blit(coins_text, (
    40 + image.get_width() + 40 + price_text.get_width() + 10 + coins_icon.get_width() + 10, text_line_height + 40))
    coins_text_right = 40 + image.get_width() + 40 + price_text.get_width() + 10 + coins_icon.get_width() + 10

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 32)
    if not bought:
        buy_button = font.render("Buy", True, "lime")
    else:
        if selected_skin == title:
            buy_button = font.render("Selected", True, "gray")
        else:
            buy_button = font.render("Select", True, pygame.Color((0, 200, 0)))
    screen.blit(buy_button, (coins_text_right + coins_text.get_width() * 3 + 10, text_line_height + 40))
    return pygame.Rect(coins_text_right + coins_text.get_width() * 3 + 10, text_line_height + 40,
                       buy_button.get_width(), buy_button.get_height())


def draw_upgrade_menu():
    # Drawing an update menu in a shop
    screen.fill("black")

    background_image = pygame.image.load("assets/images/main_menu.png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background_image, (0, 0))

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 42)
    upgrade_text = font.render("Upgrades", True, "white")
    upgrade_rect = upgrade_text.get_rect(topleft=(50, 5))

    exit_button_image = pygame.image.load("assets/buttons/exit_button.png")
    exit_button_image = pygame.transform.scale(exit_button_image, (32, 32))
    exit_button_rect = exit_button_image.get_rect(topleft=(10, 10))

    screen.blit(upgrade_text, upgrade_rect)
    screen.blit(exit_button_image, exit_button_rect)

    boss_time_icon = pygame.image.load("assets/upgrades/boss_time_icon.png")
    heart_icon = pygame.image.load("assets/upgrades/heart_icon.png")
    money_chance_icon = pygame.image.load("assets/upgrades/money_chance_icon.png")
    money_mult_icon = pygame.image.load("assets/upgrades/money_mult_icon.png")

    coin_image = Coin.images[0]
    coin_image = pygame.transform.scale(coin_image, (24, 24))

    icon_size = (48, 48)
    boss_time_icon = pygame.transform.scale(boss_time_icon, icon_size)
    heart_icon = pygame.transform.scale(heart_icon, icon_size)
    money_chance_icon = pygame.transform.scale(money_chance_icon, icon_size)
    money_mult_icon = pygame.transform.scale(money_mult_icon, icon_size)

    icon_x = 410
    icon_spacing = 5
    start_y = 30
    text_x = 50
    upgrade_bar_x = 200
    upgrade_bar_width = 100

    heart_icon_rect = heart_icon.get_rect(topleft=(icon_x, start_y))
    money_chance_icon_rect = money_chance_icon.get_rect(topleft=(icon_x, heart_icon_rect.bottom + icon_spacing))
    boss_time_icon_rect = boss_time_icon.get_rect(topleft=(icon_x, money_chance_icon_rect.bottom + icon_spacing))
    money_mult_icon_rect = money_mult_icon.get_rect(topleft=(icon_x, boss_time_icon_rect.bottom + icon_spacing))

    upgrade_name = font.render("Extra HP", True, "white")
    screen.blit(upgrade_name, (text_x - 5, start_y + 6))

    if heart_up:
        upgrade_cost_text = font.render("MAX", True, "white")
        can_upgrade_heart = False
    else:
        upgrade_cost_text = font.render(str(HEART_UPGRADE_COST), True, "white")
        can_upgrade_heart = True

    upgrade_cost_rect = upgrade_cost_text.get_rect(topleft=(upgrade_bar_x, start_y + 6))
    screen.blit(upgrade_cost_text, upgrade_cost_rect)
    screen.blit(coin_image, (upgrade_cost_rect.right + 3, start_y + 8))

    pygame.draw.rect(screen, "black", (upgrade_bar_x + upgrade_bar_width, start_y + 6, upgrade_bar_width, 30))
    if heart_up:
        pygame.draw.rect(screen, "green", (upgrade_bar_x + upgrade_bar_width, start_y + 6, upgrade_bar_width, 30),
                         width=100)

    upgrade_name = font.render("More Coins", True, "white")
    screen.blit(upgrade_name, (text_x - 30, heart_icon_rect.bottom + icon_spacing + 6))

    if money_chance_up < len(MONEY_CHANCE_UPGRADE_COSTS):
        upgrade_cost_text = font.render(str(MONEY_CHANCE_UPGRADE_COSTS[money_chance_up]), True, "white")
        can_upgrade_money_chance = True
    else:
        upgrade_cost_text = font.render("MAX", True, "white")
        can_upgrade_money_chance = False

    upgrade_cost_rect = upgrade_cost_text.get_rect(topleft=(upgrade_bar_x, heart_icon_rect.bottom + icon_spacing + 6))
    screen.blit(upgrade_cost_text, upgrade_cost_rect)
    screen.blit(coin_image, (upgrade_cost_rect.right + 5, heart_icon_rect.bottom + icon_spacing + 8))

    pygame.draw.rect(screen, "black", (
        upgrade_bar_x + upgrade_bar_width, heart_icon_rect.bottom + icon_spacing + 8, upgrade_bar_width, 30))
    pygame.draw.rect(screen, "green", (upgrade_bar_x + upgrade_bar_width, heart_icon_rect.bottom + icon_spacing + 8,
                                       upgrade_bar_width // 3 * money_chance_up, 30), width=100)

    # Boss time
    upgrade_name = font.render("Weak Boss", True, "white")
    screen.blit(upgrade_name, (text_x - 30, money_chance_icon_rect.bottom + icon_spacing + 6))

    if boss_time_up < len(BOSS_TIME_UPGRADE_COSTS):
        upgrade_cost_text = font.render(str(BOSS_TIME_UPGRADE_COSTS[boss_time_up]), True, "white")
        can_upgrade_boss_time = True
    else:
        upgrade_cost_text = font.render("MAX", True, "white")
        can_upgrade_boss_time = False

    upgrade_cost_rect = upgrade_cost_text.get_rect(
        topleft=(upgrade_bar_x, money_chance_icon_rect.bottom + icon_spacing + 6))
    screen.blit(upgrade_cost_text, upgrade_cost_rect)
    screen.blit(coin_image, (upgrade_cost_rect.right + 5, money_chance_icon_rect.bottom + icon_spacing + 8))

    pygame.draw.rect(screen, "black", (
        upgrade_bar_x + upgrade_bar_width, money_chance_icon_rect.bottom + icon_spacing + 8, upgrade_bar_width, 30))
    pygame.draw.rect(screen, "green", (
        upgrade_bar_x + upgrade_bar_width, money_chance_icon_rect.bottom + icon_spacing + 8,
        upgrade_bar_width // 3 * boss_time_up, 30), width=100)

    upgrade_name = font.render("x2 coins", True, "white")
    screen.blit(upgrade_name, (text_x - 20, boss_time_icon_rect.bottom + icon_spacing + 6))

    if money_mult_up:
        upgrade_cost_text = font.render("MAX", True, "white")
        can_upgrade_money_mult = False
    else:
        upgrade_cost_text = font.render(str(MONEY_MULT_UPGRADE_COST), True, "white")
        can_upgrade_money_mult = True

    upgrade_cost_rect = upgrade_cost_text.get_rect(
        topleft=(upgrade_bar_x, boss_time_icon_rect.bottom + icon_spacing + 6))
    screen.blit(upgrade_cost_text, upgrade_cost_rect)
    screen.blit(coin_image, (upgrade_cost_rect.right + 5, boss_time_icon_rect.bottom + icon_spacing + 8))

    pygame.draw.rect(screen, "black", (
        upgrade_bar_x + upgrade_bar_width, boss_time_icon_rect.bottom + icon_spacing + 8, upgrade_bar_width, 30))
    if money_mult_up:
        pygame.draw.rect(screen, "green", (
            upgrade_bar_x + upgrade_bar_width, boss_time_icon_rect.bottom + icon_spacing + 8, upgrade_bar_width, 30),
                         width=100)

    screen.blit(heart_icon, heart_icon_rect)
    screen.blit(money_chance_icon, money_chance_icon_rect)
    screen.blit(boss_time_icon, boss_time_icon_rect)
    screen.blit(money_mult_icon, money_mult_icon_rect)

    return exit_button_rect, heart_icon_rect, money_chance_icon_rect, boss_time_icon_rect, money_mult_icon_rect, can_upgrade_money_chance, can_upgrade_boss_time, can_upgrade_heart, can_upgrade_money_mult


def initialize_shop_data():
    # Initializing shop data if not created at the start
    default_data = {
        "heart_up": False,
        "money_chance_up": 0,
        "boss_time_up": 0,
        "money_mult_up": False
    }

    if not os.path.exists("saves/shop_save.json"):
        with open("saves/shop_save.json", "w") as f:
            json.dump(default_data, f, indent=4)


def apply_upgrades():
    # Apply all upgrades
    global heart_up, COINS_APPEND_CHANCE, COINS_VISIBILITY_LIMIT, money_chance_up, money_mult_up, boss_time_up, BOSSFIGHT_TIME
    try:
        with open("saves/shop_save.json", "r") as f:
            data = json.load(f)
            heart_up = data.get("heart_up", False)
            money_chance_up = data.get("money_chance_up", 0)
            boss_time_up = data.get("boss_time_up", 0)
            money_mult_up = data.get("money_mult_up", False)

    except FileNotFoundError:
        initialize_shop_data()
    except json.JSONDecodeError:
        pass

    if money_chance_up == 1:
        COINS_APPEND_CHANCE = 40
        COINS_VISIBILITY_LIMIT = 7
    if money_chance_up == 2:
        COINS_APPEND_CHANCE = 30
        COINS_VISIBILITY_LIMIT = 10
    if money_chance_up == 3:
        COINS_APPEND_CHANCE = 20
        COINS_VISIBILITY_LIMIT = 15

    if boss_time_up == 1:
        BOSSFIGHT_TIME = 9
    if boss_time_up == 2:
        BOSSFIGHT_TIME = 8
    if boss_time_up == 3:
        BOSSFIGHT_TIME = 7


def game_over():
    # Game over function
    global game_state, heart_up, heart, current_death_animation_index, current_reviving_smoke_index, reviving_angel_sprite, high_score

    if sound_on:
        pygame.mixer.music.stop()
    save_data()

    if heart:
        if sound_on:
            sound_effects["revival"].play()
        # If revival bought
        game_state = GAME_STATE_PLAYING
        heart = False
        reset_game(reset_score=False)
        reviving_angel_sprite.add(RevivingAngel())
        current_reviving_smoke_index = 0
        return

    if sound_on:
        sound_effects["death_sound"].play()
    if sound_on:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("sounds/background_music.mp3")
        pygame.mixer.music.play(-1, 0.0)
    reviving_angel_sprite = pygame.sprite.Group()
    current_death_animation_index = 0
    high_score = max(score, high_score)


def draw_shop():
    # Drawing shop
    screen.fill("black")

    background_image = pygame.image.load("assets/images/main_menu.png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background_image, (0, 0))

    upgrade_button_image = pygame.image.load("assets/buttons/upgrade_button.png")
    upgrade_button_image = pygame.transform.scale(upgrade_button_image, (128, 128))

    skins_button_image = pygame.image.load("assets/buttons/skins_button.png")
    skins_button_image = pygame.transform.scale(skins_button_image, (128, 128))

    exit_button_image = pygame.image.load("assets/buttons/exit_button.png")
    exit_button_image = pygame.transform.scale(exit_button_image, (32, 32))

    upgrade_button_rect = upgrade_button_image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))
    skins_button_rect = skins_button_image.get_rect(center=(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2))
    exit_button_rect = exit_button_image.get_rect(topleft=(10, 10))

    screen.blit(upgrade_button_image, upgrade_button_rect)
    screen.blit(skins_button_image, skins_button_rect)
    screen.blit(exit_button_image, exit_button_rect)

    return upgrade_button_rect, skins_button_rect, exit_button_rect


def buy_upgrade(upgrade_type, can_upgrade):
    # A function to handle buying upgrades
    global coins_count, heart_up, money_chance_up, boss_time_up, money_mult_up

    with open("saves/shop_save.json", "r") as f:
        data = json.load(f)

    if upgrade_type == "heart_up" and not heart_up and can_upgrade:
        if coins_count >= HEART_UPGRADE_COST:
            coins_count -= HEART_UPGRADE_COST
            heart_up = True
            data["heart_up"] = True
            if sound_on:
                sound_effects["buy"].play()
        else:
            if sound_on:
                sound_effects["button_click"].play()

    elif upgrade_type == "money_chance_up" and money_chance_up < 3 and can_upgrade:
        if coins_count >= MONEY_CHANCE_UPGRADE_COSTS[money_chance_up]:
            coins_count -= MONEY_CHANCE_UPGRADE_COSTS[money_chance_up]
            money_chance_up += 1
            data["money_chance_up"] = money_chance_up
            if sound_on:
                sound_effects["buy"].play()
        else:
            if sound_on:
                sound_effects["button_click"].play()

    elif upgrade_type == "boss_time_up" and boss_time_up < 3 and can_upgrade:
        if coins_count >= BOSS_TIME_UPGRADE_COSTS[boss_time_up]:
            coins_count -= BOSS_TIME_UPGRADE_COSTS[boss_time_up]
            boss_time_up += 1
            data["boss_time_up"] = boss_time_up
            if sound_on:
                sound_effects["buy"].play()
        else:
            if sound_on:
                sound_effects["button_click"].play()

    elif upgrade_type == "money_mult_up" and not money_mult_up and can_upgrade:
        if coins_count >= MONEY_MULT_UPGRADE_COST:
            coins_count -= MONEY_MULT_UPGRADE_COST
            money_mult_up = True
            data["money_mult_up"] = True
            if sound_on:
                sound_effects["buy"].play()
        else:
            if sound_on:
                sound_effects["button_click"].play()

    with open("saves/shop_save.json", "w") as f:
        json.dump(data, f, indent=4)

    save_data()
    apply_upgrades()


def shop():
    # The shop function
    global coins_count, selected_skin
    running = True
    upgrade_button_rect, skins_button_rect, exit_button_rect = draw_shop()
    upgrade_menu_exit_button_rect = None
    heart_icon_rect = None
    money_chance_icon_rect = None
    boss_time_icon_rect = None
    money_mult_icon_rect = None
    can_upgrade_money_chance = False
    can_upgrade_boss_time = False
    can_upgrade_heart = False
    can_upgrade_money_mult = False

    current_skin_animation_index = 0
    current_title = "Lizard"
    images = []
    for i in all_images[current_title]:
        images.append(pygame.transform.scale(i, (i.get_width() * 5, i.get_height() * 5)))
    data = characters

    shop_state = 0
    current_skin_animation_index = 0
    prev_skin_animation_time = -1
    current_skin_animation_image_index = 0
    skin_exit_button = pygame.Rect(10, 10, 32, 32)
    buy_button = None

    image = pygame.image.load("assets/buttons/left_button.png")
    left_button = pygame.transform.scale(image, (32, 32))
    left_button_rect = pygame.Rect(2, SCREEN_HEIGHT // 2 - left_button.get_height() // 2, left_button.get_width(),
                                   left_button.get_height())

    image = pygame.image.load("assets/buttons/right_button.png")
    right_button = pygame.transform.scale(image, (32, 32))
    right_button_rect = pygame.Rect(SCREEN_WIDTH - right_button.get_width() - 2,
                                    SCREEN_HEIGHT // 2 - right_button.get_height() // 2, right_button.get_width(),
                                    right_button.get_height())

    this_running = True

    # Shop states:
    # 0 - Main shop menu
    # 1 - Upgrades menu
    # 2 - Skins menu

    while this_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_data()
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if shop_state == 0:
                    if upgrade_button_rect.collidepoint(mouse_pos):
                        shop_state = 1
                        upgrade_menu_exit_button_rect, heart_icon_rect, money_chance_icon_rect, boss_time_icon_rect, money_mult_icon_rect, can_upgrade_money_chance, can_upgrade_boss_time, can_upgrade_heart, can_upgrade_money_mult = draw_upgrade_menu()
                        pygame.display.update()
                        if sound_on:
                            sound_effects["button_click"].play()

                    elif skins_button_rect.collidepoint(mouse_pos):
                        shop_state = 2
                        if sound_on:
                            sound_effects["button_click"].play()
                    elif exit_button_rect.collidepoint(mouse_pos):
                        global game_state
                        game_state = GAME_STATE_MENU
                        if sound_on:
                            sound_effects["button_click"].play()
                        return

                elif shop_state == 1:
                    if upgrade_menu_exit_button_rect.collidepoint(mouse_pos):
                        if sound_on:
                            sound_effects["button_click"].play()
                        shop_state = 0
                        upgrade_menu_exit_button_rect = None
                        draw_shop()
                        pygame.display.update()
                    elif heart_icon_rect.collidepoint(mouse_pos):
                        buy_upgrade("heart_up", can_upgrade_heart)
                        upgrade_menu_exit_button_rect, heart_icon_rect, money_chance_icon_rect, boss_time_icon_rect, money_mult_icon_rect, can_upgrade_money_chance, can_upgrade_boss_time, can_upgrade_heart, can_upgrade_money_mult = draw_upgrade_menu()
                    elif money_chance_icon_rect.collidepoint(mouse_pos):
                        buy_upgrade("money_chance_up", can_upgrade_money_chance)
                        upgrade_menu_exit_button_rect, heart_icon_rect, money_chance_icon_rect, boss_time_icon_rect, money_mult_icon_rect, can_upgrade_money_chance, can_upgrade_boss_time, can_upgrade_heart, can_upgrade_money_mult = draw_upgrade_menu()
                    elif boss_time_icon_rect.collidepoint(mouse_pos):
                        buy_upgrade("boss_time_up", can_upgrade_boss_time)
                        upgrade_menu_exit_button_rect, heart_icon_rect, money_chance_icon_rect, boss_time_icon_rect, money_mult_icon_rect, can_upgrade_money_chance, can_upgrade_boss_time, can_upgrade_heart, can_upgrade_money_mult = draw_upgrade_menu()
                    elif money_mult_icon_rect.collidepoint(mouse_pos):
                        buy_upgrade("money_mult_up", can_upgrade_money_mult)
                        upgrade_menu_exit_button_rect, heart_icon_rect, money_chance_icon_rect, boss_time_icon_rect, money_mult_icon_rect, can_upgrade_money_chance, can_upgrade_boss_time, can_upgrade_heart, can_upgrade_money_mult = draw_upgrade_menu()
                elif shop_state == 2:
                    if buy_button.collidepoint(mouse_pos):
                        if sound_on:
                            sound_effects["button_click"].play()
                        if not obtained_characters[current_title] and coins_count - data[current_title][1] >= 0:
                            if sound_on:
                                sound_effects["buy"].play()
                            obtained_characters[current_title] = True
                            coins_count -= data[current_title][1]
                        elif obtained_characters[current_title]:
                            selected_skin = current_title
                            player.load_frames()
                    elif skin_exit_button.collidepoint(mouse_pos):
                        if sound_on:
                            sound_effects["button_click"].play()
                        shop_state = 0
                    elif left_button_rect.collidepoint(mouse_pos):
                        if sound_on:
                            sound_effects["button_click"].play()
                        current_skin_animation_index = (current_skin_animation_index - 1) % len(characters)
                        current_title = characters_list[current_skin_animation_index]
                        current_skin_animation_image_index = 0
                        images = []
                        for i in all_images[current_title]:
                            images.append(pygame.transform.scale(i, (i.get_width() * 5, i.get_height() * 5)))
                    elif right_button_rect.collidepoint(mouse_pos):
                        if sound_on:
                            sound_effects["button_click"].play()
                        current_skin_animation_index = (current_skin_animation_index + 1) % len(characters)
                        current_title = characters_list[current_skin_animation_index]
                        current_skin_animation_image_index = 0
                        images = []
                        for i in all_images[current_title]:
                            images.append(pygame.transform.scale(i, (i.get_width() * 5, i.get_height() * 5)))

        if shop_state == 0:
            upgrade_button_rect, skins_button_rect, exit_button_rect = draw_shop()
        elif shop_state == 2:
            buy_button = draw_skins_avatar(images[current_skin_animation_image_index], current_title,
                                           data[current_title][0], data[current_title][1],
                                           bought=obtained_characters[current_title])
            if time() - prev_skin_animation_time > 0.1:
                current_skin_animation_image_index = (current_skin_animation_image_index + 1) % len(images)
                prev_skin_animation_time = time()
            screen.blit(left_button, (left_button_rect.x, left_button_rect.y))
            screen.blit(right_button, (right_button_rect.x, right_button_rect.y))

        pygame.display.update()
        clock.tick(30)


def draw_main_menu():
    # Drawing main menu
    global coins_count
    screen.fill("black")

    background_image = pygame.image.load("assets/images/main_menu.png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background_image, (0, 0))

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 58)
    title_text = font.render("Gravity Jumper", True, "white")
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 40)
    start_text = font.render("Play", True, "gray")
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    shop_text = font.render("Shop", True, "gray")
    shop_rect = shop_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 5))

    quit_text = font.render("Quit", True, "gray")
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

    screen.blit(title_text, title_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)

    font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 25)
    high_score_text = font.render(f"High score: {high_score}", True, "orange")
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2,
                                  title_rect.bottom + 5))

    sound_on_text = font.render(f"Sound: {"on" if sound_on else "off"}", True, "red" if not sound_on else "green")
    screen.blit(sound_on_text, (SCREEN_WIDTH - 5 - sound_on_text.get_width(),
                                SCREEN_HEIGHT - 5 - sound_on_text.get_height()))
    sound_on_rect = pygame.Rect(SCREEN_WIDTH - 5 - sound_on_text.get_width(),
                                SCREEN_HEIGHT - 5 - sound_on_text.get_height(),
                                sound_on_text.get_width(),
                                sound_on_text.get_height())

    if GAME_STATE_SHOP == 2:
        screen.blit(shop_text, shop_rect)

    coin_frames = Coin.images
    coin_image = coin_frames[current_main_menu_coin_frame]
    coin_image = pygame.transform.scale(coin_image, (28, 28))

    coin_text_font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 32)
    coin_text = coin_text_font.render(str(coins_count), True, "white")

    coin_image_rect = coin_image.get_rect()
    coin_text_rect = coin_text.get_rect()

    coin_image_rect.topright = (SCREEN_WIDTH - 10, 10)
    coin_text_rect.topright = (coin_image_rect.left - 5, 10)

    screen.blit(coin_image, coin_image_rect)
    screen.blit(coin_text, coin_text_rect)

    return start_rect, quit_rect, shop_rect, sound_on_rect


def handle_menu_input(position, start_rect, quit_rect, shop_rect, sound_rect):
    # If a button in the main menu is pressed
    global game_state, heart, heart_up, sound_on

    new_mouse_pos = position

    if start_rect.collidepoint(new_mouse_pos):
        if sound_on:
            sound_effects["button_click"].play()
        if heart_up:
            heart = True
        game_state = GAME_STATE_PLAYING
        reset_game()
    elif quit_rect.collidepoint(new_mouse_pos):
        if sound_on:
            sound_effects["button_click"].play()
        save_data()
        pygame.quit()
        exit()
    elif sound_rect.collidepoint(new_mouse_pos):
        sound_on = not sound_on
        if not sound_on:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.load("sounds/background_music.mp3")
            pygame.mixer.music.play()
    elif shop_rect.collidepoint(new_mouse_pos):
        if sound_on:
            sound_effects["button_click"].play()
        game_state = GAME_STATE_SHOP
        shop()


def reset_game(reset_score=True):
    # Start or reset game
    global coins, tiles_up, tiles_down, enemies, fireballs, player, coins_count, wall_render_delta, score, current_wall_images, show_hint, hint_delta, music

    coins = []
    wall_render_delta = 0
    if reset_score:
        score = 0

    if sound_on and game_state == GAME_STATE_PLAYING:
        pygame.mixer.music.load("sounds/run.mp3")
        pygame.mixer.music.play(-1, 0.0)
    enemies = pygame.sprite.Group()
    fireballs = pygame.sprite.Group()

    player.rect = pygame.Rect(20, SCREEN_HEIGHT - player.image.get_height() - 15, player.image.get_width(),
                              player.image.get_height())
    player.vx, player.vy = 0, 0
    player.up_pos = False

    current_wall_images = deque(choices(wall_images, k=4))
    tiles_up = deque()
    tiles_down = deque()

    show_hint = True
    hint_delta = 0

    for i in range(4):
        up = NormalTile((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH - wall_render_delta,
                         TILE_HEIGHT * 2))
        down = NormalTile((i * WALL_IMAGE_WIDTH + WALL_IMAGE_WIDTH // 2 - TILE_WIDTH - wall_render_delta,
                           SCREEN_HEIGHT - TILE_HEIGHT * 2))

        tiles_up.append(up)
        tiles_down.append(down)


class Player(pygame.sprite.Sprite):
    # A normal player sprite
    def __init__(self):
        # Creating the player
        super().__init__()

        # Generating frames
        self.frames = []
        self.reversed_frames = []
        self.load_frames()

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

        self.gravity_change_delta = 0.35
        self.prev_gravity_change = -1

        self.music_playing = True

    def load_frames(self):
        # Load skins
        global selected_skin
        self.frames = []
        self.reversed_frames = []

        for i in all_images[selected_skin]:
            self.frames.append(i)
            self.reversed_frames.append(i)
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

    def change_image(self):
        # Animation
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
        if self.rect.y > SCREEN_HEIGHT - 10 or self.rect.y < 0:
            game_over()

    def tiles_check(self):
        collided = False
        # Check collision with ceiling tiles (tiles_up)
        for tile in tiles_up:
            if not tile.rect.colliderect(self.rect):
                continue
            collided = True
            # Handle special tiles
            if isinstance(tile, ElectricalTile):
                if tile.activated:
                    game_over()
            elif isinstance(tile, BouncingTile):
                if self.flown:
                    continue
                if sound_on:
                    sound_effects["bounce"].play()
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
                if tile.activated:
                    game_over()
            elif isinstance(tile, BouncingTile):
                tile.bounced = True
                self.rect.y = tile.rect.top - self.rect.height
                self.reverse_jump()
                if sound_on:
                    sound_effects["bounce"].play()
                # Regular floor tile: adjust position based on movement direction
            if not isinstance(tile, BouncingTile):
                if self.vy > 0:  # Moving down into the tile
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vy < 0:  # Moving up into the tile
                    self.rect.top = tile.rect.bottom
                    self.vy = 0

        if collided or collided1 and not self.music_playing:
            self.music_playing = True
            if sound_on:
                pygame.mixer.music.load("sounds/run.mp3")
                pygame.mixer.music.play(-1, 0.0)

        # Apply gravity if no collisions and not moving
        if self.vy == 0 and not collided and not collided1:
            self.vy = -5 if self.up_pos else 5

    def coins_check(self):
        global coins_count, money_mult_up
        # Checking if a player has picked up some coins

        to_pop = []
        for i in range(len(coins)):
            if self.rect.colliderect(coins[i].rect):
                if sound_on:
                    sound_effects["coin_collected"].play()
                to_pop.append(i)
                if money_mult_up:
                    coins_count += 1
                coins_count += 1
        delta = 0
        for i in to_pop:
            coins.pop(i - delta)
            delta += 1

    def fireballs_check(self):
        # Checking fireball collisions
        global fireballs

        for i in fireballs:
            if i.rect.colliderect(self.rect):
                game_over()

    def enemies_check(self):
        # Checking enemies collision
        global enemies

        for i in enemies:
            if isinstance(i, KillingEnemy):
                if i.collision_rect.colliderect(self.rect):
                    game_over()

    def reverse_jump(self):
        # Changing gravity
        if time() - self.prev_gravity_change < self.gravity_change_delta:
            return
        pygame.mixer.music.stop()
        self.music_playing = False
        if sound_on:
            sound_effects["jump"].play()
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
        # Hitbox drawing
        pygame.draw.rect(screen, pygame.Color("green"), self.rect, width=1)


class Tile(pygame.sprite.Sprite):
    # A base tile class
    def __init__(self, position, images):
        # Creating the tile
        super().__init__()
        self.images = images
        self.prev_time = -1
        self.animation_delta = TILE_ANIMATION_DELTA

        self.current_image_index = 0
        self.image = self.images[self.current_image_index]
        self.rect = pygame.Rect(position[0], position[1], self.image.get_width(), self.image.get_height())

    def change_image(self):
        # Animation changing
        if time() - self.prev_time < self.animation_delta:
            return
        self.prev_time = time()

        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image = self.images[self.current_image_index]
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def draw(self):
        # Draw a tile
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def draw_a_hitbox(self):
        # Hitbox drawing
        pygame.draw.rect(screen, pygame.Color("blue"), self.rect, width=1)


class ElectricalTile(Tile):
    # A class for an electrical tile
    frames = []
    for file_name in os.listdir("assets/tiles_animations/electrical"):
        frames.append(pygame.transform.scale(
            pygame.image.load(f"assets/tiles_animations/electrical/{file_name}"),
            (TILE_WIDTH * ENLARGING_COEFFICIENT, TILE_HEIGHT * ENLARGING_COEFFICIENT)))
        frames[-1].set_colorkey((0, 0, 0))

    def __init__(self, position):
        # Creating the tile
        images = ElectricalTile.frames
        self.timer = randint(0, 4)
        super().__init__(position, images)
        self.image = images[self.timer]
        self.current_image_index = self.timer
        self.activated = False

    def change_image(self):
        # Animation changing
        if time() - self.prev_time < self.animation_delta:
            return
        self.prev_time = time()
        self.timer += 1
        if self.timer >= 5:
            self.animation_delta = ACTIVATED_ELECTRICAL_TILE_ANIMATION_DELTA
            self.activated = True
        if self.timer == 5 and sound_on:
            sound_effects["electrical_tile"].play()
        if self.timer >= 9:
            self.animation_delta = TILE_ANIMATION_DELTA
            self.timer = 1
            self.activated = False
        self.current_image_index = self.timer - 1
        self.image = self.images[self.current_image_index]
        self.rect = pygame.Rect(self.rect.x, self.rect.y, self.image.get_width(), self.image.get_height())

    def move(self, x, y):
        # Move on the screen
        self.rect = self.rect.move(x, y)

    def draw_a_hitbox(self):
        # Hitbox drawing
        if self.activated:
            pygame.draw.rect(screen, "green", self.rect, width=1)
        else:
            pygame.draw.rect(screen, "red", self.rect, width=1)
        font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 30)
        text = font.render(str(self.timer), True, "white")
        screen.blit(text, (self.rect.x, self.rect.y))


class NormalTile(Tile):
    # A normal tile
    frames = [pygame.transform.scale(pygame.image.load("assets/tiles_animations/normal/1.png"),
                                     (TILE_WIDTH * ENLARGING_COEFFICIENT,
                                      TILE_HEIGHT * ENLARGING_COEFFICIENT))]

    def __init__(self, position):
        # Creating the tile
        frames = NormalTile.frames
        super().__init__(position, frames)


class BouncingTile(Tile):
    # Bouncing tile class
    frames = []
    for i in os.listdir("assets/tiles_animations/bouncing"):
        frames.append(pygame.transform.scale(pygame.image.load("assets/tiles_animations/bouncing/" + i),
                                             (TILE_WIDTH * ENLARGING_COEFFICIENT,
                                              TILE_HEIGHT * ENLARGING_COEFFICIENT)))

    def __init__(self, position):
        # Creating the tile
        frames = BouncingTile.frames
        super().__init__(position, frames)
        self.current_image_index = 0
        self.image = frames[0]
        self.bounced = False

    def change_image(self):
        # Animation change
        if self.bounced:
            self.current_image_index += 1
            if self.current_image_index > 3:
                self.current_image_index = 0
                self.image = self.images[0]
                self.bounced = False
                return
            self.image = self.images[self.current_image_index]


class Coin(pygame.sprite.Sprite):
    # A class for a coin
    images = []
    for i in os.listdir("assets/frames"):
        image = pygame.image.load("assets/frames/" + i)
        if "coin_anim_f" in i:
            images.append(pygame.transform.scale(image, (ENLARGING_COEFFICIENT * image.get_width(),
                                                         ENLARGING_COEFFICIENT * image.get_height())))

    def __init__(self, x, y):
        # Creating the coin
        super().__init__()
        self.images = Coin.images
        self.image = self.images[0]
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.current_image_index = 0
        self.animation_delta = 0.1
        self.prev_animation = -1

        self.delta = 1

    def change_image(self):
        # Animating
        if time() - self.prev_animation < self.animation_delta:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image = self.images[self.current_image_index]
        self.prev_animation = time()

        self.delta = -self.delta

    def draw(self):
        # Drawing
        screen.blit(self.image, (self.rect.x, self.rect.y + self.delta))

    def draw_a_hitbox(self):
        # Hitbox drawing
        pygame.draw.rect(screen, pygame.Color("yellow"), self.rect, width=1)


class RevivingAngel(pygame.sprite.Sprite):
    # A class for a reviving angel
    def __init__(self):
        # Creating
        super().__init__()
        self.images = []
        for i in get_images("angel_idle"):
            self.images.append(pygame.transform.scale(i, (i.get_width() * 1.5,
                                                          i.get_height() * 1.5)))
        self.current_image_index = 0
        self.start_time = time()
        self.prev_animation_change = -1
        self.rect = pygame.Rect(player.rect.x - 15, player.rect.y, self.images[self.current_image_index].get_width(),
                                self.images[self.current_image_index].get_height())
        self.image = self.images[self.current_image_index]

    def change_image(self):
        # Animation
        self.rect.x, self.rect.y = player.rect.x - 15, player.rect.y
        if time() - self.start_time > 5:
            self.kill()
        if time() - self.prev_animation_change < 0.1:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image = self.images[self.current_image_index]
        self.prev_animation_change = time()


class FireEnemy(pygame.sprite.Sprite):
    # A class for an enemy which shoots with fireballs
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
        # Creating the class
        super().__init__()

        self.images = FireEnemy.images if not reversed_image else FireEnemy.reversed_images
        self.current_index = 0
        self.image = self.images[self.current_index]
        self.animation_change_rate = 0.1
        self.prev_animation_change = -1
        self.rect = pygame.Rect(position[0], position[1], self.image.get_width(), self.image.get_height())

    def change_animation(self):
        # Animating
        if time() - self.prev_animation_change < self.animation_change_rate:
            return
        self.prev_animation_change = time()
        self.current_index = (self.current_index + 1) % len(self.images)
        self.image = self.images[self.current_index]

    def move(self, x, y):
        # Movement
        self.rect = self.rect.move(x, y)

    def draw_a_hitbox(self):
        # Hitbox drawing
        pygame.draw.rect(screen, pygame.Color("red"), self.rect, width=1)


class FireBall(pygame.sprite.Sprite):
    # A class for a fireball
    images = []
    for i in os.listdir("assets/fireball"):
        image = pygame.image.load("assets/fireball/" + i)
        image = pygame.transform.flip(image, True, False)
        images.append(pygame.transform.scale(image, (image.get_width(),
                                                     image.get_height())))

    def __init__(self, position, velocity):
        # Creating the class
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
        # Animating
        if time() - self.prev_animation_time < self.animation_delay:
            return
        self.prev_animation_time = time()
        self.current_image = (self.current_image + 1) % len(self.images)
        self.image = self.images[self.current_image]

    def move(self):
        # Moving
        self.rect = self.rect.move(self.vx, self.vy)

    def draw_a_hitbox(self):
        # Drawing a hitbox
        pygame.draw.rect(screen, pygame.Color("orange"), self.rect, width=1)


class KillingEnemy(pygame.sprite.Sprite):
    # A class for an enemy which kills when touched
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
        # Creating the class
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
        # Animating
        if time() - self.prev_animation_time < self.animation_delta:
            return
        self.prev_animation_time = time()
        self.current_index = (self.current_index + 1) % len(self.images)
        if self.running:
            self.image = self.run_images[self.current_index]
        else:
            self.image = self.images[self.current_index]

    def follow_player(self):
        # Follow player function (may be disabled)
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
        # Hitbox drawing
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
    # Saving game data
    with open("saves/game_save.json", "w") as f:
        json.dump({"coins": coins_count, "high_score": max(score, high_score), "selected": selected_skin}, f)
    with open("saves/obtained.json", "w") as f:
        json.dump(obtained_characters, f)


if __name__ == "__main__":
    # Initializing the window
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = WALL_WIDTH * 3 * ENLARGING_COEFFICIENT, WALL_HEIGHT * ENLARGING_COEFFICIENT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    initialize_shop_data()
    apply_upgrades()

    heart_full_image = pygame.image.load("assets/frames/ui_heart_full.png")
    heart_empty_image = pygame.image.load("assets/frames/ui_heart_empty.png")
    heart_full_image_resized = pygame.transform.scale(heart_full_image, (28, 28))
    heart_empty_image_resized = pygame.transform.scale(heart_empty_image, (28, 28))

    # Loading all images
    WALL_IMAGE_WIDTH, WALL_IMAGE_HEIGHT = 84 * ENLARGING_COEFFICIENT, 121 * ENLARGING_COEFFICIENT
    wall_images = []
    for image in os.listdir("assets/images/wall_images"):
        wall_images.append(pygame.transform.scale(pygame.image.load("assets/images/wall_images/" + image),
                                                  (WALL_IMAGE_WIDTH, WALL_IMAGE_HEIGHT)))

    # Adding sprites

    tiles_up = deque()
    tiles_down = deque()
    coins = []
    coins_count = 0
    high_score = 0
    selected_skin = "Lizard"
    prev_show_coin_frame_time = -1
    current_show_coin_frame = -1
    show_coin_frames = Coin.images

    reviving_angel_sprite = pygame.sprite.Group()

    try:
        with open("saves/game_save.json") as f:
            all_data = json.load(f)
            coins_count += all_data["coins"]
            high_score = all_data["high_score"]
            selected_skin = all_data["selected"]
    except Exception as e:
        print("Не найден файл сохранения. Возможно, он был перенесён.")

    player_sprite = pygame.sprite.Group()
    player = Player()
    player_sprite.add(player)

    ALL_TILES = [NormalTile, BouncingTile, ElectricalTile]

    # Technical things
    clock = pygame.time.Clock()
    wall_render_delta = 0
    score = 0
    is_bossfight = False
    bossfight_time = -1

    current_death_animation_index = -1

    reviving_smoke_images = []
    for i in os.listdir("assets/reviving_smoke"):
        image = pygame.image.load("assets/reviving_smoke/" + i)
        reviving_smoke_images.append(pygame.transform.scale(image, (image.get_width() * ENLARGING_COEFFICIENT,
                                                                    image.get_height() * ENLARGING_COEFFICIENT)))
    current_reviving_smoke_index = -1
    reviving_smoke_pos = (-1, -1)
    prev_reviving_smoke_animation_time = -1

    show_hint = True
    hint_delta = 0

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if game_state == GAME_STATE_MENU:
                start_rect, quit_rect, shop_rect, sound_rect = draw_main_menu()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    handle_menu_input(event.pos, start_rect, quit_rect, shop_rect, sound_rect)
            elif game_state == GAME_STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    player.reverse_jump()
            elif game_state == GAME_STATE_SHOP:
                shop()

        for i in reviving_angel_sprite:
            i.change_image()
        if game_state == GAME_STATE_PLAYING:
            screen.fill("black")
            for i in range(len(current_wall_images)):
                screen.blit(current_wall_images[i], (i * WALL_IMAGE_WIDTH - wall_render_delta, 0))

            for i in tiles_up:
                if current_death_animation_index == -1:
                    i.rect.x -= WALLS_SPEED
                i.change_image()
                i.draw()
            for i in tiles_down:
                if current_death_animation_index == -1:
                    i.rect.x -= WALLS_SPEED
                i.change_image()
                i.draw()

            font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 32)
            rendered = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(rendered, (SCREEN_WIDTH - rendered.get_width() - 5 * ENLARGING_COEFFICIENT,
                                   rendered.get_height() - 5 * ENLARGING_COEFFICIENT))

            rendered1 = font.render(str(coins_count), True, (255, 255, 255))
            screen.blit(show_coin_frames[current_show_coin_frame],
                        (SCREEN_WIDTH - rendered1.get_width() - ENLARGING_COEFFICIENT * 20,
                         rendered.get_height() + 12 * ENLARGING_COEFFICIENT))
            screen.blit(rendered1, (SCREEN_WIDTH - rendered1.get_width() - 5 * ENLARGING_COEFFICIENT,
                                    rendered.get_height() + 10 * ENLARGING_COEFFICIENT))

            if heart_up:
                heart_x = 450
                heart_y = rendered.get_height() + 10 * ENLARGING_COEFFICIENT + 30

                if heart:
                    screen.blit(heart_full_image_resized, (heart_x, heart_y))
                else:
                    screen.blit(heart_empty_image_resized, (heart_x, heart_y))

            if show_hint:
                font = pygame.font.Font("assets/fonts/ByteBounce.ttf", 30)
                hint_text = font.render("Click to change gravity", True, "white")
                hint_text1 = font.render("You can also double jump with a delay.", True, "gray")
                screen.blit(hint_text, (200 - hint_delta, TILE_HEIGHT * 5))
                screen.blit(hint_text1, (200 - hint_delta, TILE_HEIGHT * 5 + hint_text.get_height()))
                if hint_delta >= 1000:
                    show_hint = False
                hint_delta += 4

            if current_death_animation_index == -1:
                player_sprite.draw(screen)
                player.move()
                player.tiles_check()
                player.coins_check()
            else:
                blit_x, blit_y = player.rect.centerx, player.rect.centery
                if player.rect.y > SCREEN_HEIGHT - player.rect.height:
                    blit_y = SCREEN_HEIGHT
                    blit_x = 30
                elif player.rect.y < 0:
                    blit_y = 5
                    blit_x = 30
                frame = death_frames[current_death_animation_index]
                screen.blit(frame, (blit_x - frame.get_width() // 2, blit_y - frame.get_height() // 2))
                current_death_animation_index += 1
                if current_death_animation_index == len(death_frames):
                    current_death_animation_index = -1
                    game_state = GAME_STATE_MENU
                    reset_game()
                clock.tick(30)

            # Walls rendering
            if current_death_animation_index == -1:
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
                    if randint(1, 100) >= 20:
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
                                                         (-10, dy // abs(dy) * 5)))
                                        else:
                                            fireballs.add(FireBall((i.rect.x, i.rect.y), (-10, 0)))
                                pos += 1

                tiles_up.append(up)
                tiles_down.append(down)

                wall_render_delta = 0

            if score % 20 == 0 and score != 0 and not is_bossfight:
                is_bossfight = True
                bossfight_time = time()
                player.gravity_change_delta = 0.2

            if is_bossfight and time() - bossfight_time > BOSSFIGHT_TIME:
                is_bossfight = False
                player.gravity_change_delta = 0.35
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
            reviving_angel_sprite.draw(screen)

            if current_reviving_smoke_index == 0:
                reviving_smoke_pos = (player.rect.x - 10, player.rect.y - 10)
            if current_reviving_smoke_index != -1:
                screen.blit(reviving_smoke_images[current_reviving_smoke_index], reviving_smoke_pos)
                if time() - prev_reviving_smoke_animation_time > 0.1:
                    prev_reviving_smoke_animation_time = time()
                    current_reviving_smoke_index += 1
                    if current_reviving_smoke_index == len(reviving_smoke_images):
                        current_reviving_smoke_index = -1

            if current_death_animation_index == -1:
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

        elif game_state == GAME_STATE_MENU:
            start_rect, quit_rect, shop_rect, sound_rect = draw_main_menu()
            pass

        if game_state == GAME_STATE_MENU:
            if time() - prev_main_menu_coin_animation_time > 0.1:
                current_main_menu_coin_frame = (current_main_menu_coin_frame + 1) % len(Coin.images)
                prev_main_menu_coin_animation_time = time()

        if game_state == GAME_STATE_MENU:
            start_rect, quit_rect, shop_rect, sound_rect = draw_main_menu()

        # Display drawing
        clock.tick(FPS)
        pygame.display.flip()

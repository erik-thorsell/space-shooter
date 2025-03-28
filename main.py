import pygame
import os
import random
import math
import time

# ------------------ MODULES ------------------ #
import modules.keyboard_controller as keyboard_controller
import modules.entities as entities

# ------------------ CONFIG ------------------ #
import modules.config as config
CONFIG = config.CONFIG


# Initialize the game engine
pygame.init()



# ------------------ VARIABLES ------------------ #
CONFIG["screen_width"] = pygame.display.Info().current_w
CONFIG["screen_height"] = pygame.display.Info().current_h
CONFIG["screen"] = pygame.display.set_mode([CONFIG["screen_width"], CONFIG["screen_height"]], pygame.NOFRAME) # windowed borderless
CONFIG["game_size"] = (CONFIG["screen_height"]*(386/513), CONFIG["screen_height"])
CONFIG["game_pos"] = ((CONFIG["screen_width"] - CONFIG["game_size"][0])/2, 0)

gameSize = CONFIG["game_size"]
gamePos = CONFIG["game_pos"]
screen = CONFIG["screen"]


# ------------------ MISC ------------------ #
# TITLE
pygame.display.set_caption('SPACE SHOOTER')

clock = pygame.time.Clock()

Controller = keyboard_controller.Controller()


# ------------------ STARS ------------------ #
stars = []

class Star:
    def __init__(self, x, y, size, color):
        speed = random.random()+.5
        self.x = x
        self.y = y
        self.size = (size*speed, size*speed)
        self.color = color
        self.speed = (speed-.25) * CONFIG["star_speed"]

    def draw(self):
        self.y += self.speed
        if self.y > gameSize[1]:
            self.y = 0
        screen.fill((255,255,255), (self.x, self.y, self.size[0], self.size[1]))

for i in range(CONFIG["star_count"]):
    stars.append(
        Star(
            x = random.randint(
                math.floor(gamePos[0]),
                math.floor(gamePos[0] + gameSize[0])
            ),
            y = random.randint(
                math.floor(gamePos[1]), 
                math.floor(gamePos[1] + gameSize[1])
            ),
            size = CONFIG["star_size"],
            color = CONFIG["star_color"]
        )
    )




player = entities.Player(
    x = gamePos[0] + gameSize[0]/2 - CONFIG["player_size"]/2,
    y = gamePos[1] + gameSize[1] - CONFIG["player_size"]*5
)


# ------------------ KEYBINDS ------------------ #

#single press keys
Controller.register([
    (pygame.K_ESCAPE, lambda: os._exit(0)),
    (pygame.K_1, lambda: player.change_skin(0)),
    (pygame.K_2, lambda: player.change_skin(1)),
    (pygame.K_3, lambda: player.change_skin(2)),
    (pygame.K_4, lambda: player.change_skin(3)),
    (pygame.K_5, lambda: player.change_skin(4))
])

#movement keys, holdable
Controller.register([
    (pygame.K_w, lambda: player.move("up"), player.stop_thrust),
    (pygame.K_s, lambda: player.move("down"), player.stop_thrust),
    (pygame.K_a, lambda: player.move("left"), player.stop_moving),
    (pygame.K_d, lambda: player.move("right"), player.stop_moving),
    (pygame.K_SPACE, player.shoot)
], 
    holdable=True
)


x_keys = [pygame.K_a, pygame.K_d]

y_keys = [pygame.K_w, pygame.K_s]

Controller.register(pygame.QUIT, lambda: exit())


last_spawn = pygame.time.get_ticks()

# BACKGROUND MUSIC
# get random file path from assets/music
music = random.choice(os.listdir("assets/music"))

pygame.mixer.music.load(f'assets/music/{music}')
pygame.mixer.music.set_volume(100)
# pygame.mixer.music.play(-1)

# ------------------ GAME LOOP ------------------ #
frame = 0
last_asteroid = 0
while True:

    # ------------------ EVENTS ------------------ #
    Controller.process_events(pygame.event.get())

    keys = pygame.key.get_pressed()
    if all(keys[key] for key in x_keys):
        player.stop_moving()
    if all(keys[key] for key in y_keys):
        player.stop_thrust()

    # ---------------- GAME LOGIC ---------------- #

    if pygame.time.get_ticks() - last_spawn > 5000 and len(CONFIG["enemies"]) == 0 and CONFIG["spawning_enabled"]:
        amount = 5
        for i in range(amount):
            entities.Enemy(
                x= gameSize[0]/2 + gamePos[0] + 60*i - (30*amount), 
                y= gamePos[1],
                speed=1, 
                skin=11,
                size=60
            )
        last_spawn = pygame.time.get_ticks()
    
    if pygame.time.get_ticks() - last_asteroid > 500:
        CONFIG["asteroids"].append(entities.Asteroid(random.choice([gamePos[0]-CONFIG["asteroid_size"], gamePos[0]+gameSize[0]+CONFIG["asteroid_size"]]),random.randint(0, gameSize[1]),1))
        last_asteroid = pygame.time.get_ticks()

    # ------------------ DRAWING ------------------ #


    # BACKGROUND
    screen.fill((0,0,0), (gamePos, gameSize))

    # STARS
    for star in stars:
        star.draw()

    # PROJECTILES
    for projectile in CONFIG["projectiles"]:
        projectile.check_collision(CONFIG["enemies"])
        projectile.draw()

    # ENEMIES
    for enemy in CONFIG["enemies"]:
        enemy.draw()
        enemy.check_collision(player)
        if enemy.y > gameSize[1]:
            exit()

    # PLAYER
    player.draw()

    # ASTEROIDS
    for asteroid in CONFIG["asteroids"]:
        asteroid.check_collision(player)
        asteroid.draw()

    # BLACK BORDERS
    screen.fill((0,0,0), (0, 0, gamePos[0], CONFIG["screen_height"]))
    screen.fill((0,0,0), (gamePos[0] + gameSize[0]-1, 0, CONFIG["screen_width"], CONFIG["screen_height"]))

    # update the screen
    pygame.display.flip()

    clock.tick(60)
    # frame += 1
    # if frame % 35 == 0:
    #     time.sleep(random.randint(1,15)/5)
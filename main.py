import pygame
import os
import random
import math

# ------------------ MODULES ------------------ #
import modules.keyboard_controller as keyboard_controller


# ------------------ CONFIG ------------------ #
CONFIG = {
    # GAME
    "spawning_enabled": True,

    # SCREEN
    "screen_boundary": 30, # pixles - border

    # STARS
    "star_speed": 2,
    "star_count": 1500,
    "star_size": 2,
    "star_color": (255, 255, 255),

    # PLAYER
    "player_speed": 5,
    "player_size": 50,
    "flame_update_rate": 15, # ticks
    "flame_thrust_rate": 100, # advance rate, how fast it becomes full flame
    "shoot_rate": 500, # ms
    "projectile_speed": 8,
    "projectile_hitbox": 1,

}


# Initialize the game engine
pygame.init()


# ------------------ ASSETS ------------------ #
ships_ui = pygame.image.load("./assets/ships.png")
projectiles_ui = pygame.image.load("./assets/projectiles.png")
misc_ui = pygame.image.load("./assets/misc.png")


# ------------------ VARIABLES ------------------ #
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode([screen_width, screen_height], pygame.NOFRAME) # windowed borderless
gameSize = (screen_height*(386/513), screen_height)
gamePos = ((screen_width - gameSize[0])/2, 0)


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


# ------------------ PROJECTILES ------------------ #
projectiles = []

class Projectile:
    def __init__(self, x, y, speed, skin, direction, size, hitbox):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.hitbox = hitbox
        self.skin = pygame.transform.scale(projectiles_ui.subsurface((8*skin, 0, 8, 8)), (size, size))
        projectiles.append(self)

    def _move(self):
        self.y += self.speed * self.direction

    def check_collision(self, enemies):
        for enemy in enemies:
            if (self.hitbox > 0 and
                abs(self.x - enemy.x) < self.hitbox + enemy.size/2 and abs(self.y - enemy.y) < self.hitbox + enemy.size/2):
                projectiles.remove(self)
                enemy.alive = False
                break
        

    def draw(self):
        self._move()
        screen.blit(self.skin, (self.x, self.y))


# ------------------ ENEMIES ------------------ #
enemies = []

class Enemy:
    def __init__(self, x, y, speed, skin, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.alive = True
        self.cooldown = 0
        self.explosion = 0

        # SKINS: 0-35
        row = skin // 6
        col = skin % 6
        self.skin = pygame.transform.scale(ships_ui.subsurface((8*4 + 8*col, 8*row, 8, 8)), (size, size))
        enemies.append(self)

    def _move(self):
        self.y += 50

    def check_collision(self, player):
        if (abs(self.x - player.x) < self.size/2 and abs(self.y - player.y) < self.size/2):
            exit()

    def draw(self):
        if not self.alive and pygame.time.get_ticks() - self.cooldown > 100:
            self.explosion += 1
            self.cooldown = pygame.time.get_ticks()
            if self.explosion == 4:
                enemies.remove(self)
                return
            self.skin = pygame.transform.scale(
                misc_ui.subsurface((8*8 + 8*self.explosion, 6*8, 8, 8)), (self.size, self.size)
            )
        if pygame.time.get_ticks() - self.cooldown > 1500/self.speed:
            self._move()
            self.cooldown = pygame.time.get_ticks()
        screen.blit(self.skin, (self.x, self.y))

# ------------------ PLAYER ------------------ #
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = (CONFIG["player_size"], CONFIG["player_size"])
        self.speed = CONFIG["player_speed"]
        self.direction_x = 1 # 0 = left, 1 = center, 2 = right
        self.direction_y = 0 # 0-3 different strengths of thrust, -1 = off
        self.skin = 0
        self.flame_variant = 0
        self.last_shot = 0
        self.last_direction_change = 0

    def move(self, direction):
        if direction == "up" and self.y > (gamePos[1] + CONFIG["screen_boundary"]):
            if pygame.time.get_ticks() - self.last_direction_change > CONFIG["flame_thrust_rate"]:
                self.direction_y = min(3, self.direction_y + 1)
                self.last_direction_change = pygame.time.get_ticks()
            self.y -= self.speed
        elif direction == "down" and self.y < (gamePos[1] + gameSize[1] - self.size[1] - CONFIG["screen_boundary"]):
            self.direction_y = -1 # disable thrust
            self.y += self.speed
        elif direction == "left" and self.x > (gamePos[0] + CONFIG["screen_boundary"]):
            self.x -= self.speed
            self.direction_x = 0
        elif direction == "right" and self.x < (gamePos[0] + gameSize[0] - self.size[0] - CONFIG["screen_boundary"]):
            self.x += self.speed
            self.direction_x = 2
    
    def stop_moving(self):
        self.direction_x = 1

    def stop_thrust(self):
        self.direction_y = 0

    def change_skin(self, skin):
        skin = max(0, min(skin, 4)) # 0-4, there are 5 skins
        self.skin = skin

    def shoot(self):
        if pygame.time.get_ticks() - self.last_shot < CONFIG["shoot_rate"]:
            return
        
        Projectile(
            x = self.x + self.size[0]/6,
            y = self.y,
            speed = CONFIG["projectile_speed"],
            skin = 0,
            direction = -1,
            size = 32*1.5,
            hitbox=CONFIG["projectile_hitbox"]
        )
        self.last_shot = pygame.time.get_ticks()
    
    def _animate_flame(self):
        if pygame.time.get_ticks() % CONFIG["flame_update_rate"] != 0: return
        if self.flame_variant >= 3:
            self.flame_variant = 0
        else:
            self.flame_variant += 1

    def draw(self):
        self._animate_flame()
        if self.direction_y != -1:
            flame = pygame.transform.scale(
                misc_ui.subsurface(
                    (
                        40 + # go to the flames part of the spritemap
                        8*self.flame_variant + # flame variant, animation
                        #slightly adjust the flame position based on the direction
                        (1 if self.direction_x == 0 else 0) + # left
                        (-1 if self.direction_x == 2 else 0), # right

                        8*self.direction_y, 8, 8)), self.size
                        )
            screen.blit(flame, (self.x-3, self.y + self.size[1]-6))

        ship = pygame.transform.scale(ships_ui.subsurface((8*self.direction_x, 8*self.skin, 8, 8)), self.size)
        screen.blit(ship, (self.x, self.y))

player = Player(
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
# ------------------ GAME LOOP ------------------ #
while True:

    # ------------------ EVENTS ------------------ #
    Controller.process_events(pygame.event.get())

    keys = pygame.key.get_pressed()
    if all(keys[key] for key in x_keys):
        player.stop_moving()
    if all(keys[key] for key in y_keys):
        player.stop_thrust()

    # ---------------- GAME LOGIC ---------------- #

    if pygame.time.get_ticks() - last_spawn > 5000 and len(enemies) == 0 and CONFIG["spawning_enabled"]:
        amount = 5
        for i in range(amount):
            Enemy(
                x= gameSize[0]/2 + gamePos[0] + 60*i - (30*amount), 
                y= gamePos[1],
                speed=1, 
                skin=11,
                size=60
            )
        last_spawn = pygame.time.get_ticks()

    # ------------------ DRAWING ------------------ #
    # clear the screen 
    screen.fill((10, 10, 10))


    # BACKGROUND
    screen.fill((0,0,0), (gamePos, gameSize))

    # STARS
    for star in stars:
        star.draw()

    # PROJECTILES
    for projectile in projectiles:
        projectile.check_collision(enemies)
        projectile.draw()

    # ENEMIES
    for enemy in enemies:
        enemy.draw()
        enemy.check_collision(player)
        if enemy.y > gameSize[1]:
            exit()

    # PLAYER
    player.draw()

    # update the screen
    pygame.display.flip()

    clock.tick(60)
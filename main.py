import pygame
import os
import random
import math

CONFIG = {
    # SCREEN
    "screen_boundary": 30, # pixles

    # STARS
    "star_speed": 2,
    "star_count": 25,
    "star_size": 2,
    "star_color": (255, 255, 255),

    # PLAYER
    "player_speed": 5,
    "player_size": 50
}


# Initialize the game engine
pygame.init()


# ------------------ ASSETS ------------------ #
ships_ui = pygame.image.load("./assets/ships.png")
projectiles_ui = pygame.image.load("./assets/projectiles.png")


# ------------------ VARIABLES ------------------ #
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode([screen_width, screen_height], pygame.NOFRAME) # windowed borderless
gameSize = (screen_height*(386/513), screen_height)
gamePos = ((screen_width - gameSize[0])/2, 0)


# ------------------ MISC ------------------ #
# TITLE
pygame.display.set_caption('SPACE SHOOTER')

clock = pygame.time.Clock()


# ------------------ STARS ------------------ #
stars = []

class Star:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = (size, size)
        self.color = color

    def draw(self):
        self.y += CONFIG["star_speed"]
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
    def __init__(self, x, y, speed, skin, direction, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.skin = pygame.transform.scale(projectiles_ui.subsurface((8*skin, 0, 8, 8)), (size, size))

    def _move(self):
        self.y += self.speed * self.direction

    def draw(self):
        self._move()
        screen.blit(self.skin, (self.x, self.y))


# ------------------ PLAYER ------------------ #
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = (CONFIG["player_size"], CONFIG["player_size"])
        self.speed = CONFIG["player_speed"]
        self.direction = 1 # 0 = left, 1 = center, 2 = right
        self.skin = 0
        self.last_shot = 0

    def move(self, direction):
        if direction == "up" and self.y > (gamePos[1] + CONFIG["screen_boundary"]):
            self.y -= self.speed
        elif direction == "down" and self.y < (gamePos[1] + gameSize[1] - self.size[1] - CONFIG["screen_boundary"]):
            self.y += self.speed
        elif direction == "left" and self.x > (gamePos[0] + CONFIG["screen_boundary"]):
            self.x -= self.speed
            self.direction = 0
        elif direction == "right" and self.x < (gamePos[0] + gameSize[0] - self.size[0] - CONFIG["screen_boundary"]):
            self.x += self.speed
            self.direction = 2
    
    def stop_moving(self):
        self.direction = 1

    def change_skin(self, skin):
        skin = max(0, min(skin, 4)) # 0-4, there are 5 skins
        self.skin = skin

    def shoot(self):
        if pygame.time.get_ticks() - self.last_shot < 500:
            return
        projectiles.append(
            Projectile(
                x = self.x + self.size[0]/6,
                y = self.y,
                speed = 5,
                skin = 0,
                direction = -1,
                size = 32
            )
        )
        self.last_shot = pygame.time.get_ticks()

    def draw(self):
        ship = pygame.transform.scale(ships_ui.subsurface((8*self.direction, 8*self.skin, 8, 8)), self.size)
        screen.blit(ship, (self.x, self.y))

player = Player(
    x = gamePos[0] + gameSize[0]/2 - CONFIG["player_size"]/2,
    y = gamePos[1] + gameSize[1] - CONFIG["player_size"]*5
)


# ------------------ KEYBINDS ------------------ #
keybinds = {
    pygame.K_ESCAPE: lambda: os._exit(0),
}

movement = {
    pygame.K_w: lambda: player.move("up"),
    pygame.K_s: lambda: player.move("down"),
    pygame.K_a: lambda: player.move("left"),
    pygame.K_d: lambda: player.move("right"),
    pygame.K_SPACE: player.shoot
}

key_up = {
    pygame.K_a: player.stop_moving,
    pygame.K_d: player.stop_moving,
}


# ------------------ GAME LOOP ------------------ #
while True:

    # ------------------ EVENTS ------------------ #
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                exit()

            case pygame.KEYDOWN:
                if event.key in keybinds:
                    keybinds[event.key]()
            
            case pygame.KEYUP:
                if event.key in key_up:
                    key_up[event.key]()
    
    keys = pygame.key.get_pressed()
    for key in movement:
        if keys[key]:
            movement[key]()
            
    if all(keys[key] for key in key_up): # if both keys are pressed, stop moving
        player.stop_moving()

    # ---------------- GAME LOGIC ---------------- #


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
        projectile.draw()

    # PLAYER
    player.draw()

    # update the screen
    pygame.display.flip()

    # 60 fps
    clock.tick(60)
import pygame
import random
import modules.config as config
CONFIG = config.CONFIG

# ------------------ PROJECTILES ------------------ #
projectiles = CONFIG["projectiles"]

class Projectile:
    def __init__(self, x, y, speed, skin, direction, size, hitbox):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.hitbox = hitbox
        self.skin = pygame.transform.scale(CONFIG["projectiles_ui"].subsurface((8*skin, 0, 8, 8)), (size, size))
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
        CONFIG["screen"].blit(self.skin, (self.x, self.y))


# ------------------ ENEMIES ------------------ #
enemies = CONFIG["enemies"]

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
        self.skin = pygame.transform.scale(CONFIG["ships_ui"].subsurface((8*4 + 8*col, 8*row, 8, 8)), (size, size))
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
                CONFIG["misc_ui"].subsurface((8*8 + 8*self.explosion, 6*8, 8, 8)), (self.size, self.size)
            )
        if pygame.time.get_ticks() - self.cooldown > 1500/self.speed:
            self._move()
            self.cooldown = pygame.time.get_ticks()
        CONFIG["screen"].blit(self.skin, (self.x, self.y))

# ------------------ ASTEROIDS ------------------ #

class Asteroid:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = CONFIG["asteroid_size"]
        self.time_of_birth = pygame.time.get_ticks()
        self.speed = speed
        self.image = pygame.transform.scale(CONFIG["misc_ui"].subsurface((8, 24, 8, 8)), (self.size, self.size))
        self.current_image = None
        self.rotation = 0
        self.direction = random.randint(-200,200)/100
        self.origin = self.x
        self.rect = self.image.get_rect(center=(self.x, self.y))
        CONFIG["asteroids"].append(self)

    def destroy(self):
        CONFIG["asteroids"].remove(self)

    def check_collision(self, player):
        if (abs(self.x - player.x) < self.size/1.5 and abs((self.y+10) - player.y) < self.size/1.5):
            exit()

    def draw(self):
        if pygame.time.get_ticks() - self.time_of_birth > 10000:
            self.destroy()
            return
        self.x += -1 if self.origin > (CONFIG["game_pos"][0]+CONFIG["game_size"][0]/2) else 1
        self.y += self.direction
        if self.y < -self.size or self.y > CONFIG["game_size"][1]+self.size:
            self.destroy()
            return
        self.rotation += 1
        if self.rotation >= 360:
            self.rotation = 0
        self.current_image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = self.current_image.get_rect(center=(self.x, self.y))
        CONFIG["screen"].blit(self.current_image, self.rect)



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
        if direction == "up" and self.y > (CONFIG["game_pos"][1] + CONFIG["screen_boundary"]):
            if pygame.time.get_ticks() - self.last_direction_change > CONFIG["flame_thrust_rate"]:
                self.direction_y = min(3, self.direction_y + 1)
                self.last_direction_change = pygame.time.get_ticks()
            self.y -= self.speed
        elif direction == "down" and self.y < (CONFIG["game_pos"][1] + CONFIG["game_size"][1] - self.size[1] - CONFIG["screen_boundary"]):
            self.direction_y = -1 # disable thrust
            self.y += self.speed
        elif direction == "left" and self.x > (CONFIG["game_pos"][0] + CONFIG["screen_boundary"]):
            self.x -= self.speed
            self.direction_x = 0
        elif direction == "right" and self.x < (CONFIG["game_pos"][0] + CONFIG["game_size"][0] - self.size[0] - CONFIG["screen_boundary"]):
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
                CONFIG["misc_ui"].subsurface(
                    (
                        40 + # go to the flames part of the spritemap
                        8*self.flame_variant + # flame variant, animation
                        #slightly adjust the flame position based on the direction
                        (1 if self.direction_x == 0 else 0) + # left
                        (-1 if self.direction_x == 2 else 0), # right

                        8*self.direction_y, 8, 8)), self.size
                        )
            CONFIG["screen"].blit(flame, (self.x-3, self.y + self.size[1]-6))

        ship = pygame.transform.scale(CONFIG["ships_ui"].subsurface((8*self.direction_x, 8*self.skin, 8, 8)), self.size)
        CONFIG["screen"].blit(ship, (self.x, self.y))
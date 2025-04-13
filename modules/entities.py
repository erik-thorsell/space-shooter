import pygame
import random
import modules.config as config
CONFIG = config.CONFIG

# ------------------- COLLISION ------------------- #
def check_collision(p1, p2, callback=None):
    if CONFIG["show_hitboxes"]:
        if isinstance(p1, Asteroid):
            pygame.draw.rect(CONFIG["screen"], (255, 0, 0), p1.rect, 1)
        else:
            pygame.draw.rect(CONFIG["screen"], (255, 0, 0), (p1.x, p1.y, p1.size[0], p1.size[1]), 1)
        if isinstance(p2, Asteroid):
            pygame.draw.rect(CONFIG["screen"], (255, 0, 0), p2.rect, 1)
        else:
            pygame.draw.rect(CONFIG["screen"], (255, 0, 0), (p2.x, p2.y, p2.size[0], p2.size[1]), 1)
    p1_rect = p1.rect if isinstance(p1, Asteroid) else pygame.Rect(p1.x, p1.y, p1.size[0], p1.size[1])
    p2_rect = p2.rect if isinstance(p2, Asteroid) else pygame.Rect(p2.x, p2.y, p2.size[0], p2.size[1])
    colliding = p1_rect.colliderect(p2_rect)
    if colliding and callback:
        callback(p2)
    return colliding


# ------------------ PROJECTILES ------------------ #
projectiles = CONFIG["projectiles"]

class Projectile:
    def __init__(self, x, y, speed, skin, direction, size, hitbox, owner):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction
        self.hitbox = hitbox
        self.size = (size, size)
        self.skin = pygame.transform.scale(CONFIG["projectiles_ui"].subsurface((8*skin, 0, 8, 8)), (size, size))
        self.owner = owner
        projectiles.append(self)

    def _move(self):
        self.y += self.speed * self.direction

    def destroy(self, *args):
        if self in CONFIG["projectiles"]:
            CONFIG["projectiles"].remove(self)
        self = None
        

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
        self.size = (size, size)
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

    def draw(self):
        if not self.alive and pygame.time.get_ticks() - self.cooldown > 100:
            self.explosion += 1
            self.cooldown = pygame.time.get_ticks()
            if self.explosion == 4:
                enemies.remove(self)
                return
            self.skin = pygame.transform.scale(
                CONFIG["misc_ui"].subsurface((8*8 + 8*self.explosion, 6*8, 8, 8)), (self.size[0], self.size[1])
            )
        if pygame.time.get_ticks() - self.cooldown > 1500/self.speed:
            self._move()
            self.cooldown = pygame.time.get_ticks()
        CONFIG["screen"].blit(self.skin, (self.x, self.y))

    def explode(self, projectile):
        self.alive = False
        projectile.destroy()



# ------------------ ASTEROIDS ------------------ #

class Asteroid:
    def __init__(self, x, y, speed, type="large"):
        self.x = x
        self.y = y
        self.size = (CONFIG["asteroid_size"], CONFIG["asteroid_size"]) if type == "large" else (CONFIG["asteroid_size"]//2, CONFIG["asteroid_size"]//2)
        self.time_of_birth = pygame.time.get_ticks()
        self.speed = speed
        self.image = pygame.transform.scale(CONFIG["misc_ui"].subsurface((8, 24, 8, 8)), (self.size[0], self.size[1]))
        self.current_image = None
        self.rotation = 0
        self.direction = random.randint(-200,200)/100
        self.origin = self.x
        self.small_direciton = random.randint(-200,200)/100
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.type = type
        CONFIG["asteroids"].append(self)

    def destroy(self):
        CONFIG["asteroids"].remove(self)
        self = None

    def draw(self):
        if pygame.time.get_ticks() - self.time_of_birth > CONFIG["asteroid_lifespan"]:
            self.destroy()
            return
        if self.type == "large":
            self.x += -1 if self.origin > (CONFIG["game_pos"][0]+CONFIG["game_size"][0]/2) else 1
        else:
            self.x += self.small_direciton
        self.y += self.direction
        if self.y < -self.size[0] or self.y > CONFIG["game_size"][1]+self.size[1]:
            self.destroy()
            return
        self.rotation += 1
        if self.rotation >= 360:
            self.rotation = 0
        self.current_image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = self.current_image.get_rect(center=(self.x, self.y))
        CONFIG["screen"].blit(self.current_image, self.rect)

    def explode(self, projectile):
        projectile.destroy()
        self.destroy()
        if self.type == "small":
            return
        for i in range(CONFIG["small_asteroid_count"]):
            Asteroid(
                x = self.x + random.randint(-self.size[0], self.size[0]),
                y = self.y + random.randint(-self.size[0], self.size[0]),
                speed = 1,
                type = "small"
            )




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
            hitbox=CONFIG["projectile_hitbox"],
            owner = self
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
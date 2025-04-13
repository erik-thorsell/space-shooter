import pygame

CONFIG = {
    # GAME
    "spawning_enabled": True,
    "show_hitboxes": False,

    # SCREEN
    "screen_boundary": 30, # pixles - border

    # STARS
    "star_speed": 2,
    "star_count": 500,
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

    # ASTEROIDS
    "asteroid_spawn_rate": 750, # ms
    "asteroid_size": 48,
    "small_asteroid_count": 10,
    "asteroid_lifespan": 20000,


    # ASSETS
    "ships_ui": pygame.image.load("./assets/ships.png"),
    "projectiles_ui": pygame.image.load("./assets/projectiles.png"),
    "misc_ui": pygame.image.load("./assets/misc.png"),

    # FOR TYPEHINTING, SET IN OTHER SCRIPTS
    "screen_width": 0,
    "screen_height": 0,
    "screen": None,
    "game_size": (0, 0),
    "game_pos": (0, 0),
    "projectiles": [],
    "enemies": [],
    "asteroids": [],
}
# settings.py

WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Game Settings
ZOMBIE_GROWTH_RATE = 0.0005

# ADJUSTED: Lowered from 1.0 to 0.55 so they stay further back when they attack
MAX_ZOMBIE_SCALE = 0.35 

# ADDED: This controls how low they stand. 540 keeps them near the bottom street level.
ZOMBIE_SPAWN_Y = 540

# ADDED: Controls the scale of your weapon (1.0 is original size)
GUN_SCALE = 0.65

SPAWN_COOLDOWN = 2000

SHOOT_COOLDOWN = 100   # 0.1 second delay between shots (in milliseconds)
FLASH_DURATION = 50
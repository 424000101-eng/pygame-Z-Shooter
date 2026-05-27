# enemy.py
import pygame
import os
from settings import *

class Zombie:
    def __init__(self, x, y):
        # Tip: Make sure they spawn lower on the screen (e.g., y=450 or y=500) 
        # so they look like they are standing on the street!
        self.x = x
        self.y = y
        self.scale = 0.15  # Start even smaller in the background
        self.health = 100
        self.is_attacking = False
        
        image_path = os.path.join("assets", "zombie.png")
        self.base_image = pygame.image.load(image_path).convert_alpha()
        
    def update(self, player):
        if self.scale < MAX_ZOMBIE_SCALE:
            self.scale += ZOMBIE_GROWTH_RATE
        else:
            self.is_attacking = True
            player.health -= 0.5 
            
    def draw(self, surface):
        new_width = int(self.base_image.get_width() * self.scale)
        new_height = int(self.base_image.get_height() * self.scale)
        
        scaled_image = pygame.transform.scale(self.base_image, (new_width, new_height))
        
        # FIX: Changed 'center' to 'midbottom' to keep their feet on the ground
        rect = scaled_image.get_rect(midbottom=(self.x, self.y))
        surface.blit(scaled_image, rect)
        
    def check_shot(self, mouse_pos, damage):
        new_width = int(self.base_image.get_width() * self.scale)
        new_height = int(self.base_image.get_height() * self.scale)
        
        rect = pygame.Rect(0, 0, new_width, new_height)
        # FIX: Matches the drawing hitbox positioning
        rect.midbottom = (self.x, self.y)
        
        if rect.collidepoint(mouse_pos):
            self.health -= damage
            return True
        return False
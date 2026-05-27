# player.py
import pygame
import os
from settings import *

class Player:
    def __init__(self):
        self.health = 100
        self.gun_damage = 50
        
        # Load and scale weapon asset
        gun_path = os.path.join("assets", "gun.png")
        raw_gun = pygame.image.load(gun_path).convert_alpha()
        new_w = int(raw_gun.get_width() * GUN_SCALE)
        new_h = int(raw_gun.get_height() * GUN_SCALE)
        self.gun_image = pygame.transform.scale(raw_gun, (new_w, new_h))
        
        # Load Muzzle Flash
        flash_path = os.path.join("assets", "muzzle.png")
        raw_flash = pygame.image.load(flash_path).convert_alpha()
        self.flash_image = pygame.transform.scale(raw_flash, (int(new_w * 0.4), int(new_h * 0.4)))
        
        # Animation State Trackers
        self.last_shot_time = 0
        self.recoil_offset_x = 0
        self.recoil_offset_y = 0
        self.is_recoiling = False
        self.recoil_start_time = 0
        self.show_flash = False
        self.flash_start_time = 0
        
    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= SHOOT_COOLDOWN

    def trigger_shot(self, current_time):
        self.last_shot_time = current_time
        self.show_flash = True
        self.flash_start_time = current_time
        self.is_recoiling = True
        self.recoil_start_time = current_time

    def update(self, current_time):
        if self.show_flash and (current_time - self.flash_start_time > FLASH_DURATION):
            self.show_flash = False
            
        if self.is_recoiling:
            elapsed = current_time - self.recoil_start_time
            if elapsed < SHOOT_COOLDOWN:
                if elapsed < SHOOT_COOLDOWN // 2:
                    progress = elapsed / (SHOOT_COOLDOWN // 2)
                    self.recoil_offset_y = int(progress * 25)
                    self.recoil_offset_x = int(progress * 15)
                else:
                    progress = (elapsed - (SHOOT_COOLDOWN // 2)) / (SHOOT_COOLDOWN // 2)
                    self.recoil_offset_y = int((1 - progress) * 25)
                    self.recoil_offset_x = int((1 - progress) * 15)
            else:
                self.recoil_offset_x = 0
                self.recoil_offset_y = 0
                self.is_recoiling = False
                
    def draw_ui(self, surface):
        # Calculate base gun coordinates anchored to bottom right
        base_gun_x = WIDTH - self.gun_image.get_width()
        base_gun_y = HEIGHT - self.gun_image.get_height()
        
        final_gun_x = base_gun_x + self.recoil_offset_x
        final_gun_y = base_gun_y + self.recoil_offset_y
        
        # Render Gun
        surface.blit(self.gun_image, (final_gun_x, final_gun_y))
        
        # Render Muzzle Flash
        if self.show_flash:
            # ---------------------------------------------------------
            # TUNING SLIDERS: Adjust these numbers to line up the flash!
            # ---------------------------------------------------------
            # Increase X to move it RIGHT, decrease to move it LEFT
            FLASH_OFFSET_X = 250  
            
            # Increase Y to move it DOWN, decrease to move it UP
            FLASH_OFFSET_Y = 105   
            
            flash_x = final_gun_x + FLASH_OFFSET_X
            flash_y = final_gun_y + FLASH_OFFSET_Y
            
            surface.blit(self.flash_image, (flash_x, flash_y))
        
        # HUD Health Bar
        display_health = max(0, self.health)
        pygame.draw.rect(surface, BLACK, (10, 10, 200, 20))
        pygame.draw.rect(surface, GREEN, (10, 10, display_health * 2, 20))
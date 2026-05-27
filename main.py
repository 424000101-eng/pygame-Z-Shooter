# main.py
import pygame
import random
import os
from settings import *
from player import Player
from enemy import Zombie

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Zombie Survival")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 40, bold=True)
    sub_font = pygame.font.SysFont("Arial", 25)
    
    bg_path = os.path.join("assets", "background.png")
    background = pygame.image.load(bg_path).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    player = Player()
    zombies = []
    
    zombies_to_spawn = 0
    last_spawn_time = 0
    
    def reset_game():
        nonlocal player, zombies, zombies_to_spawn, last_spawn_time
        player = Player()
        zombies = []
        zombies_to_spawn = 3
        last_spawn_time = pygame.time.get_ticks()

    reset_game()

    game_over = False
    running = True
    
    while running:
        current_time = pygame.time.get_ticks()

        # 1. Event Handling Loops
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over: 
                    # CRITICAL FIX: Only run firing calculations if click passes 0.1s cooldown boundary
                    if player.can_shoot(current_time):
                        player.trigger_shot(current_time) # Activates kickback & flash
                        
                        mouse_pos = pygame.mouse.get_pos()
                        for z in reversed(zombies):
                            if z.check_shot(mouse_pos, player.gun_damage):
                                break 
                            
            elif event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    reset_game()
                    game_over = False

        # 2. Game Core Logic Updates
        if not game_over:
            # Track gun timers for flash visibility frames and movement trajectories
            player.update(current_time) 

            if zombies_to_spawn > 0 and (current_time - last_spawn_time > SPAWN_COOLDOWN):
                zombies.append(Zombie(random.randint(100, WIDTH-100), ZOMBIE_SPAWN_Y))
                zombies_to_spawn -= 1
                last_spawn_time = current_time

            for z in zombies:
                z.update(player)
                
            zombies = [z for z in zombies if z.health > 0]
            
            if len(zombies) == 0 and zombies_to_spawn == 0:
                zombies_to_spawn = random.randint(3, 6)
                last_spawn_time = current_time

            if player.health <= 0:
                game_over = True

        # 3. Graphics Processing Framework
        screen.blit(background, (0, 0))
        
        zombies.sort(key=lambda z: z.scale)
        for z in zombies:
            z.draw(screen)
            
        player.draw_ui(screen)
        
        if not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 6, 2)
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) 
            screen.blit(overlay, (0, 0))
            
            text_title = font.render("GAME OVER", True, RED)
            text_retry = sub_font.render("Press 'R' to Retry or close window to Quit", True, WHITE)
            
            title_rect = text_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            retry_rect = text_retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            
            screen.blit(text_title, title_rect)
            screen.blit(text_retry, retry_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
import pygame
import random
import json
import os

# 1. Initialize Pygame and Mixer (for audio)
pygame.init()
pygame.mixer.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- 3D EFFECT & DIFFICULTY CONSTANTS ---
TARGET_MAX_SIZE = 150
TARGET_MIN_SIZE = 20
EXPLOSION_LIFETIME = 250  
FLASH_DURATION = 150      
LEVEL_BANNER_DURATION = 2000  # NEW: How long the level up text stays on screen (2 seconds)

# Leaderboard settings
LEADERBOARD_FILE = "leaderboard.json"

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# --- ROBOTIC/CLEAN FONTS ---
font = pygame.font.SysFont("Courier New", 32, bold=True)
large_font = pygame.font.SysFont("Courier New", 52, bold=True)

# --- ASSET LOADING SYSTEM ---
def load_graphic(filename, size, fallback_color):
    """Tries to load an image or GIF frame. If it fails, creates a colored box instead."""
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if filename == "explosion.png":
            pygame.draw.circle(surf, fallback_color, (size[0]//2, size[1]//2), size[0]//2)
            pygame.draw.circle(surf, (255, 100, 0), (size[0]//2, size[1]//2), size[0]//3)
        else:
            pygame.draw.rect(surf, fallback_color, (0, 0, size[0], size[1]), border_radius=10)
        return surf

def load_sound(filename):
    """Tries to load a sound file. If it fails, returns None to prevent crashes."""
    try:
        return pygame.mixer.Sound(filename)
    except (FileNotFoundError, pygame.error):
        return None

# Load our visual assets
bg_img = load_graphic("background.png", (WIDTH, HEIGHT), (40, 45, 60))
crosshair_img = load_graphic("crosshair.png", (40, 40), (0, 255, 0))
explosion_img = load_graphic("explosion.png", (TARGET_MAX_SIZE, TARGET_MAX_SIZE), (255, 220, 50))

target_images = [
    load_graphic("target.gif", (TARGET_MAX_SIZE, TARGET_MAX_SIZE), (255, 50, 50)),     
    load_graphic("target2.gif", (TARGET_MAX_SIZE, TARGET_MAX_SIZE), (100, 50, 255))    
]

shoot_sound = load_sound("shoot.wav")

# --- LEADERBOARD FUNCTIONS ---
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_score(name, score):
    board = load_leaderboard()
    board.append({"name": name, "score": score})
    board.sort(key=lambda x: x["score"], reverse=True)
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board[:10], f)

# --- GAME STATE MANAGEMENT ---
def reset_game():
    return {
        "health": 3,
        "score": 0,
        "level": 1,
        "targets": [], 
        "explosions": [],  
        "last_spawn_time": pygame.time.get_ticks(),
        "damage_flash_time": 0,
        "level_up_time": 0,       # NEW: Tracks when the level up freeze began
        "is_level_up_frozen": False # NEW: State flag to pause spawning/updating
    }

game_state = reset_game()
current_screen = "MENU"  
player_name = ""
score_saved = False

# --- CLEAN FLOATING SELECTION RECTS ---
btn_play = pygame.Rect(WIDTH//2 - 100, 220, 200, 40)
btn_leaderboard = pygame.Rect(WIDTH//2 - 150, 320, 300, 40)
btn_quit = pygame.Rect(WIDTH//2 - 100, 420, 200, 40)

# --- UNDERLINE SELECTION RENDERING ---
def draw_robotic_button(rect, text, mouse_pos):
    """Draws clean floating text. If hovered, draws a sleek white underline beneath it."""
    is_hovered = rect.collidepoint(mouse_pos)
    
    text_surf = font.render(text, True, (255, 255, 255))
    text_x = rect.centerx - text_surf.get_width() // 2
    text_y = rect.centery - text_surf.get_height() // 2
    screen.blit(text_surf, (text_x, text_y))
    
    if is_hovered:
        line_y = text_y + text_surf.get_height() + 4
        pygame.draw.line(screen, (255, 255, 255), (text_x, line_y), (text_x + text_surf.get_width(), line_y), 3)

running = True

# 2. Main Game Loop
while running:
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    pygame.mouse.set_visible(current_screen != "PLAYING")
    screen.blit(bg_img, (0, 0))

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif current_screen == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_play.collidepoint(mouse_pos):
                    current_screen = "NAME_INPUT"
                    player_name = ""
                elif btn_leaderboard.collidepoint(mouse_pos):
                    current_screen = "LEADERBOARD"
                elif btn_quit.collidepoint(mouse_pos):
                    running = False

        elif current_screen == "NAME_INPUT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(player_name) > 0:
                    current_screen = "PLAYING"
                    game_state = reset_game()
                    score_saved = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    current_screen = "MENU"
                else:
                    if len(player_name) < 12 and event.unicode.isprintable():
                        player_name += event.unicode

        elif current_screen == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if shoot_sound:
                    shoot_sound.play()
                
                # Disable weapon hits while the level announcement screen freeze is active
                if not game_state["is_level_up_frozen"]:
                    for target in reversed(game_state["targets"]):
                        if target['rect'].collidepoint((mouse_x, mouse_y)):
                            game_state["explosions"].append({
                                "rect": target['rect'].copy(),
                                "spawn_time": current_time
                            })
                            game_state["targets"].remove(target)
                            game_state["score"] += 1
                            
                            # --- LEVEL UP CHECK TRIGGER ---
                            new_calculated_level = min(10, (game_state["score"] // 10) + 1)
                            if new_calculated_level > game_state["level"]:
                                game_state["level"] = new_calculated_level
                                game_state["is_level_up_frozen"] = True
                                game_state["level_up_time"] = current_time
                                # Clear active targets so you start fresh on the next stage
                                game_state["targets"].clear()
                            break

        elif current_screen in ["GAME_OVER", "LEADERBOARD"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_r:
                    current_screen = "MENU"

    mouse_pos = pygame.mouse.get_pos()

    # --- SCREEN LOGIC & DRAWING ---
    if current_screen == "MENU":
        title_text = large_font.render("SPACE SHOOTER", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
        
        draw_robotic_button(btn_play, "PLAY", mouse_pos)
        draw_robotic_button(btn_leaderboard, "LEADERBOARD", mouse_pos)
        draw_robotic_button(btn_quit, "QUIT", mouse_pos)

    elif current_screen == "NAME_INPUT":
        prompt_text = font.render("ENTER YOUR NAME:", True, (255, 255, 255))
        name_text = large_font.render(player_name + "_", True, (0, 255, 255))
        hint_text = font.render("(Press ENTER to start, ESC to cancel)", True, (150, 150, 150))
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, 200))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, 280))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 400))

    elif current_screen == "LEADERBOARD":
        title_text = large_font.render("TOP 10 SCORES", True, (255, 255, 255))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        board = load_leaderboard()
        y_offset = 150
        if not board:
            empty_text = font.render("No scores yet!", True, (200, 200, 200))
            screen.blit(empty_text, (WIDTH//2 - empty_text.get_width()//2, y_offset))
        else:
            for i, entry in enumerate(board):
                entry_text = font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, (255, 255, 255))
                screen.blit(entry_text, (WIDTH//2 - 180, y_offset))
                y_offset += 40
        hint_text = font.render("Press ESC to return", True, (150, 150, 150))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 530))

    elif current_screen == "PLAYING":
        # Check if we should release the level-up freeze delay
        if game_state["is_level_up_frozen"]:
            if current_time - game_state["level_up_time"] > LEVEL_BANNER_DURATION:
                game_state["is_level_up_frozen"] = False
                # Shift spawn timer window so enemies don't dump onto screen all instantly
                game_state["last_spawn_time"] = current_time

        # Calculate current operational speeds based on current level tier
        base_spawn_rate = 1000
        base_lifetime = 1500
        current_spawn_rate = base_spawn_rate - (game_state["level"] - 1) * 80
        current_lifetime = base_lifetime - (game_state["level"] - 1) * 90

        # --- CONDITIONALLY SPAWN & UPDATE TARGETS ONLY IF NOT FROZEN ---
        if not game_state["is_level_up_frozen"]:
            # Spawn logic
            if current_time - game_state["last_spawn_time"] > current_spawn_rate:
                x = random.randint(0, WIDTH - TARGET_MAX_SIZE)
                y = random.randint(50, HEIGHT - TARGET_MAX_SIZE)
                
                target_rect = pygame.Rect(0, 0, TARGET_MIN_SIZE, TARGET_MIN_SIZE)
                center_x, center_y = x + (TARGET_MAX_SIZE // 2), y + (TARGET_MAX_SIZE // 2)
                target_rect.center = (center_x, center_y)
                
                chosen_image_index = random.randint(0, len(target_images) - 1)
                
                game_state["targets"].append({
                    'rect': target_rect, 
                    'spawn_time': current_time,
                    'anchor_center': (center_x, center_y),
                    'image_idx': chosen_image_index  
                })
                game_state["last_spawn_time"] = current_time

            # Scale/Update targets loop
            for target in reversed(game_state["targets"]):
                elapsed = current_time - target['spawn_time']
                
                if elapsed > current_lifetime:
                    game_state["targets"].remove(target)
                    game_state["health"] -= 1
                    game_state["damage_flash_time"] = current_time
                    
                    if game_state["health"] <= 0:
                        current_screen = "GAME_OVER"
                else:
                    progress = elapsed / current_lifetime
                    new_size = int(TARGET_MIN_SIZE + (TARGET_MAX_SIZE - TARGET_MIN_SIZE) * progress)
                    target['rect'].width = new_size
                    target['rect'].height = new_size
                    target['rect'].center = target['anchor_center']

        # Clean up stale explosions
        for explosion in reversed(game_state["explosions"]):
            if current_time - explosion["spawn_time"] > EXPLOSION_LIFETIME:
                game_state["explosions"].remove(explosion)

        # Draw Active Explosions
        for explosion in game_state["explosions"]:
            scaled_explosion = pygame.transform.scale(explosion_img, (explosion['rect'].width, explosion['rect'].height))
            screen.blit(scaled_explosion, explosion['rect'])

        # Draw Targets
        for target in game_state["targets"]:
            base_img = target_images[target['image_idx']]
            scaled_graphic = pygame.transform.scale(base_img, (target['rect'].width, target['rect'].height))
            screen.blit(scaled_graphic, target['rect'])

        # Draw Damage Flash Overlay
        flash_elapsed = current_time - game_state["damage_flash_time"]
        if flash_elapsed < FLASH_DURATION:
            alpha = int(120 * (1.0 - (flash_elapsed / FLASH_DURATION)))
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, alpha)) 
            screen.blit(flash_surf, (0, 0))

        # --- NEW: DRAW LEVEL UP SCREEN ANNOUNCEMENT FLOATING TEXT ---
        if game_state["is_level_up_frozen"]:
            lvl_text = large_font.render(f"ADVANCING TO LEVEL {game_state['level']}", True, (255, 255, 255))
            screen.blit(lvl_text, (WIDTH//2 - lvl_text.get_width()//2, HEIGHT//2 - lvl_text.get_height()//2))

        # Draw UI
        score_text = font.render(f"SCORE: {game_state['score']} | LVL: {game_state['level']}", True, (255, 255, 255))
        health_text = font.render(f"HEALTH: {'♥ ' * game_state['health']}", True, (255, 50, 50))
        screen.blit(score_text, (20, 10))
        screen.blit(health_text, (WIDTH - 240, 10))

        # Draw Crosshair
        crosshair_rect = crosshair_img.get_rect(center=(mouse_x, mouse_y))
        screen.blit(crosshair_img, crosshair_rect)

    elif current_screen == "GAME_OVER":
        if not score_saved:
            save_score(player_name, game_state["score"])
            score_saved = True

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        go_text = large_font.render("GAME OVER", True, (255, 50, 50))
        score_text = font.render(f"Final Score: {game_state['score']} (Level {game_state['level']})", True, (255, 255, 255))
        hint_text = font.render("Press ESC or R to return to Menu", True, (200, 200, 200))
        
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2 + 80))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
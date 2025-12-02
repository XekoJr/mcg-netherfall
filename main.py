import pygame
import sys
from assets import *
from player import Player
from enemy_manager import EnemyManager
from xp import xp_drops
from menu import Menu
from projectile import projectiles
from game_manager import GameManager

pygame.init()
pygame.mixer.init()
initialize_fonts()

# Verify that fonts were initialized
if font_button is None or font_title is None or font_credit is None or font_score is None:
    # Create fonts directly if the initialization failed
    font_title = pygame.font.Font(pygame.font.match_font('arial'), 50)
    font_button = pygame.font.Font(pygame.font.match_font('arial'), 30)
    font_credit = pygame.font.Font(pygame.font.match_font('arial'), 20)
    font_score = pygame.font.Font(pygame.font.match_font('arial'), 25)
    font_health = pygame.font.Font(pygame.font.match_font('arial'), 25)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# Initialize the menu
menu = Menu(screen, font_title, font_button, font_credit, font_score)

# Globals for the current player and enemy manager
current_player = None
current_enemy_manager = None

def reset_game(achievements=None):
    """Reset the game state, including the player, enemies, projectiles, and abilities."""
    global current_player, current_enemy_manager
    projectiles.clear()
    xp_drops.clear()

    settings = menu.load_settings()
    if achievements is None:
        achievements = settings.get("achievements", {})  # Use provided achievements if available

    fonts = {
        'credit': font_credit,
        'score': font_score,
        'health': font_health
    }
    current_player = Player(fonts=fonts)
    skills = settings.get("skills", {})
    current_player.initialize_abilities(skills)
    current_player.apply_skill_upgrades(skills)
    current_player.apply_stat_upgrades(skills)

    current_enemy_manager = EnemyManager()
    current_enemy_manager.enemies.clear()

    return current_player, current_enemy_manager, achievements

# Add reset_game method to Menu class for use in GameManager
menu.reset_game = reset_game
menu.save_settings = menu.save_settings

if __name__ == "__main__":
    # Create game manager
    game_manager = GameManager(screen, menu)
    
    # Set up the initial game state
    current_player, current_enemy_manager, achievements = reset_game()
    
    # Start the game from the main menu
    menu.main_menu(
        current_player, 
        current_enemy_manager, 
        reset_game, 
        game_manager.run_game_loop, 
        achievements
    )

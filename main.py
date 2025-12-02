import pygame
import sys
from assets import *
from player import Player
from managers import EnemyManager, GameManager
from xp import xp_drops
from menu import Menu
from projectile import projectiles

pygame.init()
pygame.mixer.init()
initialize_fonts()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vampire Survivors Clone")

# Initialize the menu with Fonts class attributes
menu = Menu(screen, Fonts.title, Fonts.button, Fonts.credit, Fonts.score)

# Globals for the current player and enemy manager
current_player = None
current_enemy_manager = None

def reset_game(achievements=None):
    """Reset game state - clears enemies, projectiles, and resets player."""
    global current_player, current_enemy_manager
    projectiles.clear()
    xp_drops.clear()

    settings = menu.load_settings()
    if achievements is None:
        achievements = settings.get("achievements", {})  # Use provided achievements if available

    fonts = {
        'credit': Fonts.credit,
        'score': Fonts.score,
        'health': Fonts.health
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

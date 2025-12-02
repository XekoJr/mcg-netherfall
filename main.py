import pygame
import sys
from assets import *
from ui.utils import show_loading_screen
from managers import EnemyManager, GameManager, SaveManager
from xp import xp_drops
from ui import Menu
from projectile import projectiles
from characters import Ranger, Gigachad

pygame.init()
pygame.mixer.init()
initialize_fonts()
pygame.display.set_caption("MCG Netherfall")

# Initialize save manager and display
save_manager = SaveManager(save_file="save/save.dat")
screen = Menu.initialize_display(save_manager)

show_loading_screen(
    screen,
    image_path='./assets/images/background/background-production-loading.png',
    duration=1.5
)

menu = Menu(screen, Fonts.title, Fonts.button, Fonts.credit, Fonts.score)

# Globals for the current player and enemy manager
current_player = None
current_enemy_manager = None

def reset_game(achievements=None, character_type="ranger"):
    """Reset game with selected character."""
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
    
    # Create character based on type
    if character_type == "gigachad":
        current_player = Gigachad(fonts=fonts)
    else:  # Default to ranger
        current_player = Ranger(fonts=fonts)
    
    skills = settings.get("skills", {})
    current_player.initialize_abilities(skills)
    current_player.apply_skill_upgrades(skills)
    current_player.apply_stat_upgrades(skills)

    current_enemy_manager = EnemyManager()
    current_enemy_manager.enemies.clear()

    return current_player, current_enemy_manager, achievements

game_manager = GameManager(screen, menu)

# Set callbacks
menu.reset_game = reset_game
menu.game_loop = game_manager.run_game_loop

if __name__ == "__main__":
    # Set up the initial game state
    current_player, current_enemy_manager, achievements = reset_game()
    
    # Start the game from the main menu
    menu.main_menu(current_player, current_enemy_manager, achievements)

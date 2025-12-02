import pygame

# ============================================================================
# SCREEN & MAP CONSTANTS
# ============================================================================
WIDTH, HEIGHT = 1366, 768
MAP_WIDTH = 3000
MAP_HEIGHT = 3000

# ============================================================================
# COLORS
# ============================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (169, 169, 169)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)

# ============================================================================
# FONTS
# ============================================================================
class Fonts:
    """Container for game fonts."""
    title = None
    button = None
    credit = None
    health = None
    score = None

def initialize_fonts():
    """Initialize all game fonts."""
    Fonts.title = pygame.font.Font(pygame.font.match_font('arial'), 50)
    Fonts.button = pygame.font.Font(pygame.font.match_font('arial'), 30)
    Fonts.credit = pygame.font.Font(pygame.font.match_font('arial'), 20)
    Fonts.health = pygame.font.Font(pygame.font.match_font('arial'), 25)
    Fonts.score = pygame.font.Font(pygame.font.match_font('arial'), 25)

# ============================================================================
# IMAGES
# ============================================================================
try:
    background_image = pygame.image.load('./assets/images/background/background-ingame-final.png')
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill((50, 50, 50))

# ============================================================================
# AUDIO
# ============================================================================
pygame.mixer.init()

# Music
main_menu_music = None
game_music = None
boss_music = None
skill_music = None

# UI Sounds
hover_sound = None
click_sound = None

# Combat Sounds
normal_hit_sound = None
crit_hit_sound = None
block_hit_sound = None

# XP & Level Sounds
collect_xp_sound = None
level_up_sound = None
skill_bought_sound = None
skill_failed_sound = None

# Player Sounds
hurt_sound = None
death_sound = None

# Ability Sounds
ability_obtained_sound = None
ability_used_sound = None

# Enemy Sounds
bat_death_sound = None
skeleton_death_sound = None
blob_death_sound = None
boss_death_sound = None
boss_spawn_sound = None

try:
    # Music
    main_menu_music = pygame.mixer.Sound('./assets/audio/main-menu-music.wav') 
    game_music = pygame.mixer.Sound('./assets/audio/ingame-music.wav')         
    boss_music = pygame.mixer.Sound('./assets/audio/boss-music.wav')
    skill_music = pygame.mixer.Sound('./assets/audio/skill-music.mp3')           

    # Menu Interaction
    hover_sound = pygame.mixer.Sound('./assets/audio/menu-hover.wav')          
    click_sound = pygame.mixer.Sound('./assets/audio/menu-click.wav')          

    # Sound effects
    # Projectile sounds
    normal_hit_sound = pygame.mixer.Sound('./assets/audio/normal-hit.wav')    
    crit_hit_sound = pygame.mixer.Sound('./assets/audio/crit-hit.wav')      
    block_hit_sound = pygame.mixer.Sound('./assets/audio/block_hit.mp3')  

    # xp and level up sounds
    collect_xp_sound = pygame.mixer.Sound('./assets/audio/xp-collect.wav')    
    level_up_sound = pygame.mixer.Sound('./assets/audio/level-up.wav')   
    skill_bought_sound = pygame.mixer.Sound('./assets/audio/skill-bought.mp3')
    skill_failed_sound = pygame.mixer.Sound('./assets/audio/skill-failed.mp3') 

    # Player sounds
    hurt_sound = pygame.mixer.Sound('./assets/audio/hurt.wav')               
    death_sound = pygame.mixer.Sound('./assets/audio/death/player-death.wav')
        
    # Ability sounds
    ability_obtained_sound = pygame.mixer.Sound('./assets/audio/ability-obtained.wav')
    ability_used_sound = pygame.mixer.Sound('./assets/audio/ability-used.wav')         

    # Enemy sounds
    bat_death_sound = pygame.mixer.Sound('./assets/audio/death/bat-death.wav')
    skeleton_death_sound = pygame.mixer.Sound('./assets/audio/death/skeleton-death.wav')
    blob_death_sound = pygame.mixer.Sound('./assets/audio/death/blob-death.wav')
    boss_death_sound = pygame.mixer.Sound('./assets/audio/death/boss-death.wav')
    boss_spawn_sound = pygame.mixer.Sound('./assets/audio/boss-spawn.wav')

except pygame.error as e:
    print(f"Error loading sounds: {e}")
    main_menu_music = None 
    game_music = None
    boss_music = None
    skill_music = None

    button_hover_sound = None
    button_click_sound = None
    
    normal_hit_sound = None
    crit_hit_sound = None
    block_hit_sound = None

    collect_xp_sound = None
    level_up_sound = None
    skill_bought_sound = None
    skill_failed_sound = None

    hurt_sound = None
    death_sound = None

    ability_obtained_sound = None
    ability_used_sound = None

    bat_death_sound = None
    boss_death_sound = None
    skeleton_death_sound = None
    blob_death_sound = None
    boss_spawn_sound = None

import pygame

# SCREEN & MAP CONSTANTS
WIDTH, HEIGHT = 1366, 768
MAP_WIDTH = 3000  # 150 tiles * 20 pixels
MAP_HEIGHT = 3000  # 150 tiles * 20 pixels

# COLORS
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

# FONTS
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

# IMAGES
try:
    background_image = pygame.image.load('./assets/images/background/background-ingame-final.png')
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill((50, 50, 50))

# TILESET BACKGROUND IMAGES (should be 600x600 pixels = 30x30 tiles at 20px each)
# Note: If your source images are 300x300, they will be scaled to 600x600
TILESET_BACKGROUNDS = {}
try:
    # Load and scale tileset backgrounds to 600x600 pixels
    bg_1 = pygame.image.load('./assets/images/textures/tileset-backgrounds/tileset-bg-1.png')
    TILESET_BACKGROUNDS["bg-1"] = pygame.transform.scale(bg_1, (600, 600))
    
    bg_2 = pygame.image.load('./assets/images/textures/tileset-backgrounds/tileset-bg-2.png')
    TILESET_BACKGROUNDS["bg-2"] = pygame.transform.scale(bg_2, (600, 600))
    
    bg_cross = pygame.image.load('./assets/images/textures/tileset-backgrounds/tileset-bg-cross.png')
    TILESET_BACKGROUNDS["bg-cross"] = pygame.transform.scale(bg_cross, (600, 600))
    
    bg_path_h = pygame.image.load('./assets/images/textures/tileset-backgrounds/tileset-bg-path-horizontal.png')
    TILESET_BACKGROUNDS["bg-path-horizontal"] = pygame.transform.scale(bg_path_h, (600, 600))
    
    bg_path_v = pygame.image.load('./assets/images/textures/tileset-backgrounds/tileset-bg-path-vertical.png')
    TILESET_BACKGROUNDS["bg-path-vertical"] = pygame.transform.scale(bg_path_v, (600, 600))
    
except pygame.error as e:
    print(f"✗ ERROR loading tileset backgrounds: {e}")

# PROP IMAGES (decorative objects)
PROP_IMAGES = {}
try:
    # Bushes (1x1 tile = 20x20 pixels)
    PROP_IMAGES["bush-1"] = pygame.image.load('./assets/images/textures/bushes/bush-1.png')
    PROP_IMAGES["bush-2"] = pygame.image.load('./assets/images/textures/bushes/bush-2.png')
    PROP_IMAGES["bush-3"] = pygame.image.load('./assets/images/textures/bushes/bush-3.png')
    PROP_IMAGES["bush-4"] = pygame.image.load('./assets/images/textures/bushes/bush-4.png')
    
    # Rocks (1x1 tile = 20x20 pixels)
    PROP_IMAGES["rock-1"] = pygame.image.load('./assets/images/textures/rocks/rock-1.png')
    PROP_IMAGES["rock-2"] = pygame.image.load('./assets/images/textures/rocks/rock-2.png')
    PROP_IMAGES["rock-3"] = pygame.image.load('./assets/images/textures/rocks/rock-3.png')
    
    # Big rocks (2x2 tiles = 40x40 pixels)
    PROP_IMAGES["big-rock-1"] = pygame.image.load('./assets/images/textures/rocks/big-rock-1.png')
    PROP_IMAGES["big-rock-2"] = pygame.image.load('./assets/images/textures/rocks/big-rock-2.png')
    
    # Square props (1x1 or 2x2 tiles)
    PROP_IMAGES["barrel-1"] = pygame.image.load('./assets/images/textures/square-props/barrel-1.png')
    PROP_IMAGES["box-1"] = pygame.image.load('./assets/images/textures/square-props/box-1.png')
    PROP_IMAGES["box-2"] = pygame.image.load('./assets/images/textures/square-props/box-2.png')
    PROP_IMAGES["vase-1"] = pygame.image.load('./assets/images/textures/square-props/vase-1.png')
    PROP_IMAGES["vase-2"] = pygame.image.load('./assets/images/textures/square-props/vase-2.png')
    PROP_IMAGES["chest-close"] = pygame.image.load('./assets/images/textures/square-props/chest-close.png')
    PROP_IMAGES["chest-open"] = pygame.image.load('./assets/images/textures/square-props/chest-open.png')
    PROP_IMAGES["stone-rip-1"] = pygame.image.load('./assets/images/textures/square-props/stone-rip-1.png')
    PROP_IMAGES["stone-rip-2"] = pygame.image.load('./assets/images/textures/square-props/stone-rip-2.png')
    PROP_IMAGES["stone-text"] = pygame.image.load('./assets/images/textures/square-props/stone-text.png')
    
    # Big props (2x2 tiles = 40x40 pixels)
    PROP_IMAGES["big-well"] = pygame.image.load('./assets/images/textures/square-props/big-well.png')
    PROP_IMAGES["big-spawnner"] = pygame.image.load('./assets/images/textures/square-props/big-spawnner.png')  # Non-collidable
    
    # Horizontal props (2x3 tiles = 40x60 pixels)
    PROP_IMAGES["bench-h"] = pygame.image.load('./assets/images/textures/horizontal-props/bench.png')
    PROP_IMAGES["coffin-h"] = pygame.image.load('./assets/images/textures/horizontal-props/coffin.png')
    
    # Vertical props (3x2 tiles = 60x40 pixels)
    PROP_IMAGES["bench-v-1"] = pygame.image.load('./assets/images/textures/vertical-props/bench-1.png')
    PROP_IMAGES["bench-v-2"] = pygame.image.load('./assets/images/textures/vertical-props/bench-2.png')
    PROP_IMAGES["coffin-v"] = pygame.image.load('./assets/images/textures/vertical-props/coffin.png')
    PROP_IMAGES["pillar-1"] = pygame.image.load('./assets/images/textures/vertical-props/pillar-1.png')
    PROP_IMAGES["pillar-2"] = pygame.image.load('./assets/images/textures/vertical-props/pillar-2.png')
    PROP_IMAGES["pillar-3"] = pygame.image.load('./assets/images/textures/vertical-props/pillar-3.png')
    PROP_IMAGES["statue"] = pygame.image.load('./assets/images/textures/vertical-props/statue.png')
    
except pygame.error as e:
    print(f"✗ ERROR loading prop images: {e}")

# AUDIO
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

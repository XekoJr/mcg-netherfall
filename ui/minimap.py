import pygame
from assets import MAP_WIDTH, MAP_HEIGHT, WHITE, BLACK, GREEN, RED, BLUE, DARK_RED

class Minimap:
    """Minimap display for world navigation."""
    
    def __init__(self, screen, translations_func, size=150, position="top-right"):
        """Initialize the minimap."""
        self.screen = screen
        self.t = translations_func
        self.size = size
        self.position = position
        self.border_thickness = 2
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent black
        
        # Scale factors
        self.scale_x = self.size / MAP_WIDTH
        self.scale_y = self.size / MAP_HEIGHT
        
    def get_position(self, screen):
        """Get the minimap position based on screen size."""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        margin = 10
        
        if self.position == "top-right":
            return (screen_width - self.size - margin, margin)
        elif self.position == "top-left":
            return (margin, margin)
        elif self.position == "bottom-right":
            return (screen_width - self.size - margin, screen_height - self.size - margin)
        elif self.position == "bottom-left":
            return (margin, screen_height - self.size - margin)
        
        return (screen_width - self.size - margin, margin)  # Default top-right
    
    def world_to_minimap(self, x, y):
        """Convert world coordinates to minimap coordinates."""
        mini_x = int(x * self.scale_x)
        mini_y = int(y * self.scale_y)
        return mini_x, mini_y
    
    def draw(self, screen, player, enemies, xp_drops, boss_projectiles):
        """Draw the minimap with all entities."""
        map_x, map_y = self.get_position(screen)
        
        # Create semi-transparent surface
        minimap_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        minimap_surface.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(minimap_surface, WHITE, (0, 0, self.size, self.size), self.border_thickness)
        
        font = pygame.font.Font(None, 20)
        title_text = font.render(self.t('minimap.title'), True, WHITE)
        minimap_surface.blit(title_text, (5, 5))
        
        # Draw XP drops (small blue dots)
        for xp in xp_drops:
            mini_x, mini_y = self.world_to_minimap(xp['x'], xp['y'])
            if 0 <= mini_x < self.size and 0 <= mini_y < self.size:
                pygame.draw.circle(minimap_surface, BLUE, (mini_x, mini_y), 1)
        
        # Draw enemies (red dots)
        for enemy in enemies:
            mini_x, mini_y = self.world_to_minimap(enemy.x, enemy.y)
            if 0 <= mini_x < self.size and 0 <= mini_y < self.size:
                # Bosses are bigger
                radius = 4 if hasattr(enemy, 'shoot_at_player') else 2
                pygame.draw.circle(minimap_surface, RED, (mini_x, mini_y), radius)
        
        # Draw boss projectiles (orange dots)
        for proj in boss_projectiles:
            mini_x, mini_y = self.world_to_minimap(proj['x'], proj['y'])
            if 0 <= mini_x < self.size and 0 <= mini_y < self.size:
                pygame.draw.circle(minimap_surface, (255, 165, 0), (mini_x, mini_y), 2)
        
        # Draw player (green dot - always on top)
        player_mini_x, player_mini_y = self.world_to_minimap(player.x, player.y)
        pygame.draw.circle(minimap_surface, GREEN, (player_mini_x, player_mini_y), 3)
        
        # Blit the minimap surface to the screen
        screen.blit(minimap_surface, (map_x, map_y))
        
        # Optional: Draw player level on minimap
        font = pygame.font.Font(None, 16)
        level_text = font.render(f"Lv.{player.level}", True, WHITE)
        screen.blit(level_text, (map_x + 5, map_y + self.size - 20))
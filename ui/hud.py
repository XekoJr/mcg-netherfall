import pygame
from assets import WHITE, Fonts

class HUD:
    """Manages all on-screen UI elements during gameplay."""
    
    def __init__(self, screen, font, translations_func):
        """Initialize the HUD."""
        self.screen = screen
        self.font = font
        self.t = translations_func  # Translation function from Menu
        self.show_debug = False  # Toggle for debug hitboxes
        
    def draw_health(self, screen, player):
        """Draw health hearts at bottom-left."""
        player.draw_health(screen)
        
    def draw_score(self, screen, player):
        """Draw score at top-left."""
        if player.font_score:
            score_text = player.font_score.render(self.t('hud.score', score=player.score), True, WHITE)
            screen.blit(score_text, (20, 25))  # Top-left position
        
    def draw_xp_bar(self, screen, player):
        """Draw XP bar at top-center."""
        player.draw_xp(screen)
        
    def draw_abilities(self, screen, player):
        """Draw active ability icons."""
        player.draw_status_abilities_icons(screen)
        
    def draw_all(self, screen, player):
        """Draw all HUD elements."""
        self.draw_health(screen, player)
        self.draw_score(screen, player)
        self.draw_xp_bar(screen, player)
        self.draw_abilities(screen, player)
        
    def toggle_debug(self):
        """Toggle debug hitbox display."""
        self.show_debug = not self.show_debug
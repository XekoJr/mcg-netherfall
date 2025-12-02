"""Common UI elements and utilities."""

import pygame
from assets import DARK_RED, RED, WHITE, hover_sound

class Button:
    """Reusable button component."""
    
    def __init__(self, x, y, width, height, text, font, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False
        self.last_hover_state = False
        
    def update(self, mouse_pos):
        """Update button hover state."""
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Play sound when hover state changes
        if self.hovered and not was_hovered:
            hover_sound.play()
            
    def draw(self, screen):
        """Draw the button."""
        color = DARK_RED if self.hovered else RED
        pygame.draw.rect(screen, color, self.rect)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
    def handle_click(self, mouse_pos):
        """Handle button click."""
        if self.rect.collidepoint(mouse_pos) and self.action:
            return self.action()
        return None

def draw_debug_hitboxes(screen, player, enemies, projectiles, boss_projectiles, camera_x, camera_y):
    """Draw hitboxes for debugging."""
    # Player hitbox
    player_hitbox = player.get_hitbox()
    pygame.draw.rect(screen, RED, (
        player_hitbox.x - camera_x,
        player_hitbox.y - camera_y,
        player_hitbox.width,
        player_hitbox.height
    ), 2)
    
    # Enemy hitboxes
    for enemy in enemies:
        enemy_rect = enemy.get_rect()
        pygame.draw.rect(screen, RED, (
            enemy_rect.x - camera_x,
            enemy_rect.y - camera_y,
            enemy_rect.width,
            enemy_rect.height
        ), 2)
    
    # Projectile hitboxes
    for projectile in projectiles:
        pygame.draw.rect(screen, RED, (
            projectile['x'] - camera_x - 5,
            projectile['y'] - camera_y - 5,
            10, 10
        ), 2)
    
    # Boss projectile hitboxes
    for projectile in boss_projectiles:
        pygame.draw.rect(screen, RED, (
            projectile['x'] - camera_x,
            projectile['y'] - camera_y,
            60, 25
        ), 2)
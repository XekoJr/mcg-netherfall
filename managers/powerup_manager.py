import pygame
import random
from powerups import (
    MagnetPowerup, BombPowerup, SpeedPowerup, 
    RagePowerup, HealPowerup
)

class PowerupManager:
    """Manages powerup drops and active powerup effects."""
    
    def __init__(self):
        self.powerup_drops = []  # Powerups on the ground
        self.active_powerups = []  # Currently active powerup effects
        
        # Powerup drop rates (only if purchased)
        self.drop_rates = {
            'magnet': 0.05,  # 5% chance
            'bomb': 0.03,    # 3% chance
            'speed': 0.04,   # 4% chance
            'rage': 0.04,    # 4% chance
            'heal': 0.06     # 6% chance
        }
        
        # Powerup classes
        self.powerup_classes = {
            'magnet': MagnetPowerup,
            'bomb': BombPowerup,
            'speed': SpeedPowerup,
            'rage': RagePowerup,
            'heal': HealPowerup
        }
    
    def spawn_powerup(self, x, y, powerup_type=None, purchased_powerups=None):
        """Spawn a powerup at the given position."""
        if purchased_powerups is None:
            purchased_powerups = {}
        
        # Filter available powerups based on purchases
        available = {k: v for k, v in self.drop_rates.items() 
                    if purchased_powerups.get(k, False)}
        
        if not available:
            return  # No powerups purchased
        
        # Choose powerup type
        if powerup_type is None or powerup_type not in available:
            powerup_type = random.choices(
                list(available.keys()),
                weights=list(available.values()),
                k=1
            )[0]
        
        # Create powerup instance
        powerup_class = self.powerup_classes[powerup_type]
        powerup = powerup_class()
        
        self.powerup_drops.append({
            'x': x,
            'y': y,
            'type': powerup_type,
            'powerup': powerup,
            'spawn_time': pygame.time.get_ticks()
        })
    
    def try_drop_powerup(self, x, y, purchased_powerups):
        """Try to drop a powerup based on drop rates."""
        # Roll for each purchased powerup type
        for powerup_type, drop_rate in self.drop_rates.items():
            if purchased_powerups.get(powerup_type, False):
                if random.random() < drop_rate:
                    self.spawn_powerup(x, y, powerup_type, purchased_powerups)
                    break  # Only one powerup per drop
    
    def update(self, player, enemies, xp_drops):
        """Update all powerup drops and active effects."""
        # Check for player collision with powerup drops
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        
        for drop in self.powerup_drops[:]:
            drop_rect = pygame.Rect(drop['x'], drop['y'], 40, 40)
            
            if player_rect.colliderect(drop_rect):
                # Pick up powerup
                powerup = drop['powerup']
                powerup.activate(player, enemies, xp_drops)
                
                # Add to active powerups
                self.active_powerups.append(powerup)
                
                # Remove from drops
                self.powerup_drops.remove(drop)
                
                # Play sound effect (if available)
                # pickup_sound.play()
        
        # Update active powerup effects
        for powerup in self.active_powerups[:]:
            powerup.update(player, enemies, xp_drops)
            
            if powerup.is_expired():
                self.active_powerups.remove(powerup)
    
    def draw_drops(self, screen, camera_x, camera_y):
        """Draw powerup drops on the ground."""
        for drop in self.powerup_drops:
            screen_x = int(drop['x'] - camera_x)
            screen_y = int(drop['y'] - camera_y)
            
            # Draw powerup icon
            screen.blit(drop['powerup'].icon, (screen_x, screen_y))
            
            # Draw pulsing glow effect
            pulse = abs(pygame.time.get_ticks() / 500 % 1)
            glow_radius = int(25 + pulse * 10)
            alpha = int(100 * (1 - pulse))
            
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (255, 255, 255, alpha),
                (glow_radius, glow_radius),
                glow_radius,
                2
            )
            screen.blit(glow_surface, (screen_x + 20 - glow_radius, screen_y + 20 - glow_radius))
    
    def draw_effects(self, screen, camera_x, camera_y, player):
        """Draw visual effects for all active powerups."""
        for powerup in self.active_powerups:
            powerup.draw_effect(screen, camera_x, camera_y, player)
    
    def draw_active_powerups_ui(self, screen):
        """Draw active powerup icons and timers in UI."""
        x_start = screen.get_width() - 60
        y_start = 100
        spacing = 50
        
        for i, powerup in enumerate(self.active_powerups):
            if powerup.is_instant:
                continue  # Don't show instant powerups
            
            y = y_start + i * spacing
            
            # Draw icon
            screen.blit(powerup.icon, (x_start, y))
            
            # Draw remaining time
            remaining = powerup.get_remaining_time()
            time_text = pygame.font.Font(None, 20).render(f"{remaining:.1f}s", True, (255, 255, 255))
            screen.blit(time_text, (x_start + 5, y + 45))
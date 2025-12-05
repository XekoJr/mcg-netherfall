import pygame
import math
from powerups.powerup import Powerup

class MagnetPowerup(Powerup):
    """Magnet powerup that attracts all XP to the player."""
    
    def __init__(self):
        super().__init__(
            name="XP Magnet",
            description="Attracts all XP on the map to you",
            icon_path="./assets/images/powerups/magnet.png",
            duration=5,
            is_instant=False
        )
        self.pull_speed = 15  # Speed at which XP moves to player
    
    def activate(self, player, enemies=None, xp_drops=None):
        """Activate magnet effect."""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
        if xp_drops:
            # Create particles around player
            self.create_particles(
                player.x + player.size // 2,
                player.y + player.size // 2,
                (0, 191, 255),  # Deep sky blue
                count=30,
                speed=3
            )
    
    def update(self, player, enemies=None, xp_drops=None):
        """Pull all XP towards player."""
        if not self.active or not xp_drops:
            return
        
        player_center_x = player.x + player.size // 2
        player_center_y = player.y + player.size // 2
        
        # Pull each XP drop towards player
        for xp in xp_drops:
            dx = player_center_x - xp['x']
            dy = player_center_y - xp['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 5:  # Don't move if very close
                # Normalize and apply pull speed
                dx = (dx / distance) * self.pull_speed
                dy = (dy / distance) * self.pull_speed
                
                xp['x'] += dx
                xp['y'] += dy
                
                # Create trail particles
                if distance > 50:  # Only create particles if far enough
                    self.create_particles(
                        xp['x'], xp['y'],
                        (0, 255, 255),  # Cyan
                        count=1,
                        speed=0.5
                    )
        
        # Update particles
        self.update_particles()
        
        # Check if all XP has been collected
        if len(xp_drops) == 0:
            self.active = False
    
    def draw_effect(self, screen, camera_x, camera_y, player):
        """Draw magnet visual effect."""
        if not self.active:
            return
        
        # Draw particles
        self.draw_particles(screen, camera_x, camera_y)
        
        # Draw pulsing circle around player
        player_screen_x = player.x + player.size // 2 - camera_x
        player_screen_y = player.y + player.size // 2 - camera_y
        
        pulse = abs(math.sin(pygame.time.get_ticks() / 200))
        radius = int(40 + pulse * 20)
        
        # Draw multiple circles for glow effect
        for i in range(3):
            alpha = int(100 * (1 - i / 3))
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                circle_surface,
                (0, 191, 255, alpha),
                (radius, radius),
                radius - i * 5,
                2
            )
            screen.blit(circle_surface, (player_screen_x - radius, player_screen_y - radius))
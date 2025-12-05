import pygame
import random
import math
from powerups.powerup import Powerup

class SpeedPowerup(Powerup):
    """Speed powerup that increases player movement speed."""
    
    def __init__(self):
        super().__init__(
            name="Speed Boost",
            description="Increases movement speed for 10 seconds",
            icon_path="./assets/images/powerups/speed.png",
            duration=10,
            is_instant=False
        )
        self.speed_multiplier = 1.5  # 50% speed increase
        self.original_speed = 0
        self.particle_timer = 0
    
    def activate(self, player, enemies=None, xp_drops=None):
        """Activate speed boost."""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.original_speed = player.speed
        player.speed *= self.speed_multiplier
        self.particle_timer = 0
    
    def update(self, player, enemies=None, xp_drops=None):
        """Maintain speed boost and create particles."""
        if not self.active:
            return
        
        # Create green particles around player
        self.particle_timer += 1
        if self.particle_timer >= 3:  # Create particles every 3 frames
            self.create_particles(
                player.x + player.size // 2 + random.randint(-20, 20),
                player.y + player.size // 2 + random.randint(-20, 20),
                (0, 255, 0),  # Green
                count=2,
                speed=1
            )
            self.particle_timer = 0
        
        # Update particles
        self.update_particles()
        
        # Check if expired
        if self.is_expired():
            player.speed = self.original_speed
            self.active = False
    
    def draw_effect(self, screen, camera_x, camera_y, player):
        """Draw speed boost visual effect."""
        if not self.active:
            return
        
        # Draw particles
        self.draw_particles(screen, camera_x, camera_y)
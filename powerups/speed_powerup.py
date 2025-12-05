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
        
        # Draw speed lines behind player
        player_screen_x = player.x + player.size // 2 - camera_x
        player_screen_y = player.y + player.size // 2 - camera_y
        
        # Get player direction from last movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = -1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = -1
        
        # Draw speed lines
        if dx != 0 or dy != 0:
            for i in range(3):
                line_length = 20 + i * 10
                alpha = int(150 - i * 50)
                
                end_x = player_screen_x + dx * line_length
                end_y = player_screen_y + dy * line_length
                
                pygame.draw.line(
                    screen,
                    (0, 255, 0, alpha),
                    (player_screen_x, player_screen_y),
                    (end_x, end_y),
                    3 - i
                )
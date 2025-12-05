import pygame
import random
from powerups.powerup import Powerup

class RagePowerup(Powerup):
    """Rage powerup that increases attack/fire rate."""
    
    def __init__(self):
        super().__init__(
            name="Rage",
            description="Increases attack speed for 10 seconds",
            icon_path="./assets/images/powerups/rage.png",
            duration=10,
            is_instant=False
        )
        self.attack_speed_multiplier = 0.5  # 50% faster (lower cooldown)
        self.original_fire_rate = 0
        self.original_attack_cooldown = 0
        self.particle_timer = 0
    
    def activate(self, player, enemies=None, xp_drops=None):
        """Activate rage mode."""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.particle_timer = 0
        
        # Store original values and apply buff
        if hasattr(player, 'fire_rate'):  # Ranger
            self.original_fire_rate = player.fire_rate
            player.fire_rate = int(player.fire_rate * self.attack_speed_multiplier)
        
        if hasattr(player, 'attack_cooldown'):  # Gigachad
            self.original_attack_cooldown = player.attack_cooldown
            player.attack_cooldown = int(player.attack_cooldown * self.attack_speed_multiplier)
    
    def update(self, player, enemies=None, xp_drops=None):
        """Maintain rage mode and create particles."""
        if not self.active:
            return
        
        # Create purple particles around player
        self.particle_timer += 1
        if self.particle_timer >= 3:  # Create particles every 3 frames
            self.create_particles(
                player.x + player.size // 2 + random.randint(-20, 20),
                player.y + player.size // 2 + random.randint(-20, 20),
                (138, 43, 226),  # Purple
                count=2,
                speed=1
            )
            self.particle_timer = 0
        
        # Update particles
        self.update_particles()
        
        # Check if expired
        if self.is_expired():
            # Restore original values
            if hasattr(player, 'fire_rate'):
                player.fire_rate = self.original_fire_rate
            if hasattr(player, 'attack_cooldown'):
                player.attack_cooldown = self.original_attack_cooldown
            self.active = False
    
    def draw_effect(self, screen, camera_x, camera_y, player):
        """Draw rage visual effect."""
        if not self.active:
            return
        
        # Draw particles
        self.draw_particles(screen, camera_x, camera_y)
        
        # Draw pulsing aura around player
        player_screen_x = player.x + player.size // 2 - camera_x
        player_screen_y = player.y + player.size // 2 - camera_y
        
        pulse = abs(pygame.time.get_ticks() / 300 % 1)
        radius = int(35 + pulse * 15)
        alpha = int(100 * (1 - pulse))
        
        circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            circle_surface,
            (138, 43, 226, alpha),  # Purple with alpha
            (radius, radius),
            radius,
            3
        )
        screen.blit(circle_surface, (player_screen_x - radius, player_screen_y - radius))
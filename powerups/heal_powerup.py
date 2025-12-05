import pygame
from powerups.powerup import Powerup

class HealPowerup(Powerup):
    """Heal powerup that restores player health."""
    
    def __init__(self):
        super().__init__(
            name="Health Pack",
            description="Restores 50% of max health",
            icon_path="./assets/images/powerups/heal.png",
            duration=0,
            is_instant=True
        )
        self.heal_percent = 0.5  # 50% of max health
        self.animation_duration = 1000  # 1 second animation
    
    def activate(self, player, enemies=None, xp_drops=None):
        """Activate healing."""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
        # Calculate and apply heal
        heal_amount = int(player.max_health * self.heal_percent)
        player.health = min(player.max_health, player.health + heal_amount)
        
        # Create red/pink healing particles
        self.create_particles(
            player.x + player.size // 2,
            player.y + player.size // 2,
            (255, 105, 180),  # Hot pink
            count=30,
            speed=2
        )
    
    def update(self, player, enemies=None, xp_drops=None):
        """Update healing animation."""
        if not self.active:
            return
        
        # Update particles
        self.update_particles()
        
        # Continue for animation duration
        current_time = pygame.time.get_ticks()
        if (current_time - self.start_time) >= self.animation_duration:
            self.active = False
    
    def draw_effect(self, screen, camera_x, camera_y, player):
        """Draw healing visual effect."""
        if not self.active:
            return
        
        # Draw particles only
        self.draw_particles(screen, camera_x, camera_y)
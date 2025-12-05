import pygame
import math
from powerups.powerup import Powerup
from assets import MAP_WIDTH, MAP_HEIGHT

class BombPowerup(Powerup):
    """Bomb powerup that damages all enemies in expanding radius."""
    
    def __init__(self):
        super().__init__(
            name="Bomb",
            description="Deals massive damage to all enemies",
            icon_path="./assets/images/powerups/bomb.png",
            duration=0,
            is_instant=True
        )
        self.damage = 150  # Base damage
        self.max_radius = 800  # Maximum explosion radius
        self.current_radius = 0
        self.expansion_speed = 20  # Pixels per frame
        self.player_pos = (0, 0)
        self.damaged_enemies = set()  # Track which enemies have been damaged
    
    def activate(self, player, enemies=None, xp_drops=None):
        """Activate bomb explosion."""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.current_radius = 0
        self.player_pos = (player.x + player.size // 2, player.y + player.size // 2)
        self.damaged_enemies.clear()
        
        # Create explosion particles
        self.create_particles(
            self.player_pos[0],
            self.player_pos[1],
            (255, 100, 0),  # Orange
            count=50,
            speed=5
        )
    
    def update(self, player, enemies=None, xp_drops=None):
        """Expand explosion and damage enemies."""
        if not self.active:
            return
        
        # Expand explosion radius
        self.current_radius += self.expansion_speed
        
        # Damage enemies within radius
        if enemies:
            for enemy in enemies:
                enemy_id = id(enemy)
                
                # Skip if already damaged
                if enemy_id in self.damaged_enemies:
                    continue
                
                # Calculate distance to enemy
                enemy_center_x = enemy.x + enemy.size[0] // 2
                enemy_center_y = enemy.y + enemy.size[1] // 2
                
                dx = enemy_center_x - self.player_pos[0]
                dy = enemy_center_y - self.player_pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                
                # Check if enemy is within explosion radius
                if distance <= self.current_radius:
                    enemy.take_damage(self.damage)
                    self.damaged_enemies.add(enemy_id)
                    
                    # Create impact particles
                    self.create_particles(
                        enemy_center_x,
                        enemy_center_y,
                        (255, 0, 0),  # Red
                        count=10,
                        speed=3
                    )
        
        # Update particles
        self.update_particles()
        
        # Deactivate when explosion reaches max size
        if self.current_radius >= self.max_radius:
            self.active = False
    
    def draw_effect(self, screen, camera_x, camera_y, player):
        """Draw explosion visual effect."""
        if not self.active:
            return
        
        # Draw particles
        self.draw_particles(screen, camera_x, camera_y)
        
        # Draw expanding explosion circle
        screen_x = int(self.player_pos[0] - camera_x)
        screen_y = int(self.player_pos[1] - camera_y)
        
        # Draw multiple circles
        for i in range(3):
            offset = i * 10
            radius = max(0, int(self.current_radius - offset))
            
            if radius > 0:
                # Calculate alpha based on distance from center
                alpha = int(150 * (1 - (self.current_radius / self.max_radius)))
                
                circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                color = (255, 100 + i * 50, 0, alpha)  # Orange to yellow
                
                pygame.draw.circle(
                    circle_surface,
                    color,
                    (radius, radius),
                    radius,
                    5 - i
                )
                
                screen.blit(circle_surface, (screen_x - radius, screen_y - radius))
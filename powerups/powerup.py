import pygame
import random
import math
from abc import ABC, abstractmethod

class Powerup(ABC):
    """Base class for all powerups."""
    
    def __init__(self, name, description, icon_path, duration=0, is_instant=True):
        """Initialize powerup."""
        self.name = name
        self.description = description
        self.icon_path = icon_path
        self.duration = duration  # seconds
        self.is_instant = is_instant
        self.active = False
        self.start_time = 0
        
        # Load icon
        try:
            self.icon = pygame.image.load(icon_path)
            self.icon = pygame.transform.scale(self.icon, (40, 40))
        except (pygame.error, FileNotFoundError):
            print(f"Could not load powerup icon: {icon_path}")
            # Create placeholder icon
            self.icon = pygame.Surface((40, 40))
            self.icon.fill((128, 128, 128))
        
        # Animation properties
        self.animation_time = 0
        self.particles = []
    
    @abstractmethod
    def activate(self, player, enemies=None, xp_drops=None):
        """Activate the powerup effect."""
        pass
    
    @abstractmethod
    def update(self, player, enemies=None, xp_drops=None):
        """Update powerup effect (called every frame while active)."""
        pass
    
    @abstractmethod
    def draw_effect(self, screen, camera_x, camera_y, player):
        """Draw visual effects for the powerup."""
        pass
    
    def is_expired(self):
        """Check if powerup effect has expired."""
        if self.is_instant:
            return not self.active
        
        if not self.active:
            return True
        
        current_time = pygame.time.get_ticks()
        return (current_time - self.start_time) / 1000 >= self.duration
    
    def get_remaining_time(self):
        """Get remaining duration in seconds."""
        if self.is_instant or not self.active:
            return 0
        
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.start_time) / 1000
        return max(0, self.duration - elapsed)
    
    def create_particles(self, x, y, color, count=10, speed=2):
        """Create particle effect at position."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            velocity_x = math.cos(angle) * random.uniform(0.5, speed)
            velocity_y = math.sin(angle) * random.uniform(0.5, speed)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': velocity_x,
                'vy': velocity_y,
                'life': 1.0,  # 0 to 1
                'color': color,
                'size': random.randint(3, 8)
            })
    
    def update_particles(self):
        """Update particle positions and lifetimes."""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.02
            particle['size'] = max(1, particle['size'] - 0.1)
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, screen, camera_x, camera_y):
        """Draw all particles."""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'][:3], alpha) if len(particle['color']) == 4 else particle['color']
            
            screen_x = int(particle['x'] - camera_x)
            screen_y = int(particle['y'] - camera_y)
            
            pygame.draw.circle(
                screen,
                color[:3],  # RGB only for pygame.draw
                (screen_x, screen_y),
                int(particle['size'])
            )
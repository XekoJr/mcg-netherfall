import pygame
import math
from characters.character import Character
from assets import *

class Gigachad(Character):
    """Melee character that deals AOE damage around them."""
    
    def __init__(self, fonts=None, tile_manager=None):
        super().__init__(fonts, tile_manager)
        
        # Gigachad stats - tankier but slower
        self.health = 60
        self.max_health = 60
        self.base_health = 60
        self.speed = 1.5
        self.base_speed = 1.5
        
        # Combat stats
        self.attack_range = 80  # AOE radius
        self.attack_damage = 10
        self.base_attack_damage = 10
        self.attack_cooldown = 800  # Milliseconds between attacks
        self.base_attack_cooldown = 800
        self.last_attack_time = 0
        
        # Visual effect for attack
        self.attacking = False
        self.attack_animation_duration = 200
        self.attack_start_time = 0
        
        # Load character sprites (use different sprite set)
        self.player_images = {
            'down': [pygame.image.load(f'./assets/images/Gigachad/down/{i}.png') for i in range(4)],
            'up': [pygame.image.load(f'./assets/images/Gigachad/up/{i}.png') for i in range(4)],
            'left': [pygame.image.load(f'./assets/images/Gigachad/left/{i}.png') for i in range(4)],
            'right': [pygame.image.load(f'./assets/images/Gigachad/right/{i}.png') for i in range(4)],
        }
        
        # Scale images
        self.player_images = {
            direction: [pygame.transform.scale(image, (self.size, self.size)) for image in images]
            for direction, images in self.player_images.items()
        }

    def attack(self, camera_x, camera_y):
        """Deal AOE damage around the character."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.attacking = True
            self.attack_start_time = current_time
            self.last_attack_time = current_time
            
            # Play attack sound
            if normal_hit_sound:
                normal_hit_sound.play()

    def get_attack_area(self):
        """Get the attack area as a circle around the character."""
        return pygame.Rect(
            self.x + self.size // 2 - self.attack_range,
            self.y + self.size // 2 - self.attack_range,
            self.attack_range * 2,
            self.attack_range * 2
        )

    def is_enemy_in_range(self, enemy):
        """Check if enemy is within attack range."""
        char_center_x = self.x + self.size // 2
        char_center_y = self.y + self.size // 2
        enemy_center_x = enemy.x + enemy.size[0] // 2
        enemy_center_y = enemy.y + enemy.size[1] // 2
        
        distance = math.sqrt(
            (char_center_x - enemy_center_x) ** 2 + 
            (char_center_y - enemy_center_y) ** 2
        )
        
        return distance <= self.attack_range

    def update_attack_animation(self):
        """Update attack animation state."""
        current_time = pygame.time.get_ticks()
        if self.attacking and current_time - self.attack_start_time > self.attack_animation_duration:
            self.attacking = False

    def draw_with_offset(self, screen, camera_x, camera_y):
        """Draw character with attack visual effect."""
        super().draw_with_offset(screen, camera_x, camera_y)
        
        # Draw attack radius when attacking
        if self.attacking:
            # Semi-transparent red circle
            attack_surface = pygame.Surface((self.attack_range * 2, self.attack_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                attack_surface, 
                (255, 0, 0, 80),  # Red with transparency
                (self.attack_range, self.attack_range), 
                self.attack_range
            )
            screen.blit(
                attack_surface, 
                (self.x + self.size // 2 - self.attack_range - camera_x,
                 self.y + self.size // 2 - self.attack_range - camera_y)
            )

    def apply_upgrade(self, upgrade):
        """Apply Gigachad-specific upgrades."""
        super().apply_upgrade(upgrade)
        
        if upgrade == "damage":
            self.attack_damage = int(self.attack_damage * 1.3)
        elif upgrade == "fire_rate":  # For Gigachad, this reduces attack cooldown
            self.attack_cooldown = max(300, self.attack_cooldown * 0.85)

    def apply_stat_upgrades(self, skills):
        """Apply skill tree stat upgrades."""
        if "max_health" in skills:
            level = skills["max_health"].get("level", 0)
            self.max_health = self.base_health + (20 * level)
            self.health = self.max_health

        if "speed" in skills:
            level = skills["speed"].get("level", 0)
            self.speed = self.base_speed + (0.15 * level)  # Slightly slower speed gain

        if "damage" in skills:
            level = skills["damage"].get("level", 0)
            self.attack_damage = self.base_attack_damage + (3 * level)  # More damage per level

        if "fire_rate" in skills:
            level = skills["fire_rate"].get("level", 0)
            self.attack_cooldown = self.base_attack_cooldown - (50 * level)
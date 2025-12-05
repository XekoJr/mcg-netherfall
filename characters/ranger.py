import pygame
import math
from characters.character import Character
from projectile import fire_projectile

class Ranger(Character):
    """Ranged character that shoots projectiles."""
    
    def __init__(self, fonts=None, tile_manager=None):
        super().__init__(fonts, tile_manager)
        
        # Combat stats
        self.fire_rate = 1200
        self.base_fire_rate = 1200
        self.last_shot_time = 0
        self.projectile_damage = 6
        self.base_projectile_damage = 6
        self.crit_chance = 0
        self.base_crit_chance = 0
        self.crit_damage = 1.5
        self.base_crit_damage = 1.5
        
        # Load character sprites
        self.player_images = {
            'down': [pygame.image.load(f'assets/images/player/down/{i}.png') for i in range(4)],
            'up': [pygame.image.load(f'assets/images/player/up/{i}.png') for i in range(4)],
            'left': [pygame.image.load(f'assets/images/player/left/{i}.png') for i in range(4)],
            'right': [pygame.image.load(f'assets/images/player/right/{i}.png') for i in range(4)],
        }
        
        # Scale images
        self.player_images = {
            direction: [pygame.transform.scale(image, (self.size, self.size)) for image in images]
            for direction, images in self.player_images.items()
        }

    def attack(self, camera_x, camera_y):
        """Fire a projectile toward mouse position."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.fire_rate:
            fire_projectile(self, camera_x, camera_y)
            self.last_shot_time = current_time

    def apply_upgrade(self, upgrade):
        """Apply ranger-specific upgrades."""
        super().apply_upgrade(upgrade)
        
        if upgrade == "fire_rate":
            self.fire_rate = max(200, self.fire_rate * 0.8)
        elif upgrade == "damage":
            self.projectile_damage = int(self.projectile_damage * 1.3)
        elif upgrade == "crit_chance":
            self.crit_chance = min(200, self.crit_chance + 5)

    def apply_stat_upgrades(self, skills):
        """Apply skill tree stat upgrades."""
        if "max_health" in skills:
            level = skills["max_health"].get("level", 0)
            self.max_health = self.base_health + (20 * level)
            self.health = self.max_health

        if "speed" in skills:
            level = skills["speed"].get("level", 0)
            self.speed = self.base_speed + (0.2 * level)

        if "damage" in skills:
            level = skills["damage"].get("level", 0)
            self.projectile_damage = self.base_projectile_damage + (2 * level)

        if "fire_rate" in skills:
            level = skills["fire_rate"].get("level", 0)
            self.fire_rate = self.base_fire_rate - (50 * level)

        if "crit_chance" in skills:
            level = skills["crit_chance"].get("level", 0)
            self.crit_chance = self.base_crit_chance + (2.5 * level)

        if "crit_damage" in skills:
            level = skills["crit_damage"].get("level", 0)
            self.crit_damage = self.crit_damage + (0.15 * level)
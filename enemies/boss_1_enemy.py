import random
from enemies.enemy import Enemy
import pygame
import math
from projectile import boss_projectiles, boss_projectile_frames

class Boss1Enemy(Enemy):
    """Boss enemy with unique behaviors."""
    def __init__(self, x, y):
        images = [
            pygame.image.load(f'./assets/images/enemies/boss_1/{i}.png') for i in range(26)
        ]
        super().__init__(x, y, hp=500, speed=1, xp_value=30, damage=40, size=(150, 150), images=images)
        self.shoot_interval = 2200  # Default interval between shots
        self.default_shoot_interval = 2200  # Save default interval for resetting
        self.first_shot_delay = 1500
        self.spawn_time = pygame.time.get_ticks()
        self.last_shot_time = pygame.time.get_ticks() + self.first_shot_delay
        self.shots_fired = 0  # Tracks how many shots have been fired in total

        self.burn_damage = 5  # Damage per tick
        self.burn_duration = 3  # Poison lasts x seconds
        self.burn_tick_interval = 0.5  # Damage every x seconds

    def shoot_at_player(self, player):
        """Shoot a projectile towards a random location near the player's position."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_interval:

            # Define the random zone around the player
            offset_range = 75
            random_offset_x = random.uniform(-offset_range, offset_range)
            random_offset_y = random.uniform(-offset_range, offset_range)

            # Target a random location in the zone around the player
            target_x = player.x + player.size // 2 + random_offset_x
            target_y = player.y + player.size // 2 + random_offset_y

            # Calculate direction to the random target
            dx = target_x - (self.x + self.size[0] // 2)
            dy = target_y - (self.y + self.size[1] // 2)
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > 0:
                dx /= distance
                dy /= distance

            # Calculate angle for projectile rotation
            angle = math.degrees(math.atan2(-dy, dx))

            # Append new projectile with adjusted properties
            boss_projectiles.append({
                'x': self.x + self.size[0] // 2,
                'y': self.y + self.size[1] // 2,
                'dx': dx,
                'dy': dy,
                'damage': self.damage,
                'speed': 3,
                'frames': boss_projectile_frames,
                'frame_index': 0,
                'last_frame_time': pygame.time.get_ticks(),
                'angle': angle
            })

            # Update the time of the last shot
            self.last_shot_time = current_time
            self.shots_fired += 1  # Increment the shot counter

            # Adjust the shooting interval every 5 shots
            if self.shots_fired % 5 == 0:
                self.shoot_interval = max(500, self.shoot_interval - 35)  # Reduce interval but not below 500ms

            # Reset the shooting interval after 5 cycles of reduced intervals
            if self.shots_fired % 6 == 0:  # After 25 shots (5 intervals of 5 shots)
                self.shoot_interval = self.default_shoot_interval
                self.shots_fired = 0
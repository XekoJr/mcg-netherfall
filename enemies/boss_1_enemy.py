import random
from enemies.enemy import Enemy
import pygame
import math
from projectile import boss_projectiles, boss_projectile_frames

class Boss1Enemy(Enemy):
    """Boss enemy with unique behaviors."""
    def __init__(self, x, y, tile_manager=None):
        images = [
            pygame.image.load(f'./assets/images/enemies/boss_1/{i}.png') for i in range(26)
        ]
        super().__init__(x, y, hp=1000, speed=1, xp_value=30, damage=40, size=(150, 150), images=images, tile_manager=tile_manager)
        self.shoot_frame = 19  # Shoot when animation reaches this frame
        self.has_shot_this_cycle = False  # Track if we've already shot on this frame
        self.shots_fired = 0  # Tracks how many shots have been fired in total

        self.burn_damage = 5  # Damage per tick
        self.burn_duration = 3  # Poison lasts x seconds
        self.burn_tick_interval = 0.5  # Damage every x seconds

    def shoot_at_player(self, player):
        """Check if animation is on shooting frame and fire if so."""
        # Shoot when animation reaches frame 19, but only once per cycle
        if self.current_image_index == self.shoot_frame and not self.has_shot_this_cycle:
            # Random zone around the player
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

            # Mark that we've shot on this frame
            self.has_shot_this_cycle = True
            self.shots_fired += 1
        
        # Reset the shot flag when we move past the shooting frame
        elif self.current_image_index != self.shoot_frame:
            self.has_shot_this_cycle = False
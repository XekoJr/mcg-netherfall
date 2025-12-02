import math
import pygame
import random
from enemies.enemy import Enemy
from enemies.skeleton_enemy import SkeletonEnemy

class Boss2Enemy(Enemy):
    """Boss that spawns skeleton enemies and maintains a radius around the player."""
    def __init__(self, x, y, spawn_radius=200, num_skeletons=3, skeleton_cooldown=280):
        images = [
            pygame.image.load(f'./assets/images/enemies/boss_2/{i}.png') for i in range(56)
        ]
        super().__init__(x, y, hp=1000, speed=2, xp_value=200, damage=20, size=(150, 150), images=images)
        self.spawn_radius = spawn_radius
        self.num_skeletons = num_skeletons
        self.skeleton_cooldown = skeleton_cooldown
        self.cooldown_timer = 0

        # Animation settings
        self.current_image_index = 0
        self.animation_counter = 0  # Tracks frames to control speed
        self.animation_speed = 5  # Number of game frames per animation frame

        # First attack delay settings
        self.first_attack_delay = 260  # Delay for the first attack in frames

    def move_relative_to_player(self, player_x, player_y, playable_area):
        """Keeps a specific distance from the player."""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Set a larger distance for the boss to maintain
        desired_distance = self.spawn_radius + 200  # Radius
        margin = 50  # Margin to start moving away

        if distance > desired_distance:  # Get closer
            if distance > 0:
                dx /= distance
                dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed
        elif distance < desired_distance - margin:  # Move away
            if distance > 0:
                dx /= distance
                dy /= distance
            self.x -= dx * self.speed
            self.y -= dy * self.speed

        # Ensure Arcanos does not leave the playable area
        self.x = max(playable_area[0], min(self.x, playable_area[2]))
        self.y = max(playable_area[1], min(self.y, playable_area[3]))

    def spawn_skeletons(self, enemy_manager):
        """Spawns skeleton enemies around the player."""
        if self.first_attack_delay > 0:
            self.first_attack_delay -= 1  # Count down the first attack delay
            return  # Skip spawning until the delay is over

        if self.cooldown_timer <= 0:
            for _ in range(self.num_skeletons):
                angle = random.uniform(0, 360)
                offset_x = self.spawn_radius * random.uniform(0.8, 1.2) * math.cos(math.radians(angle))
                offset_y = self.spawn_radius * random.uniform(0.8, 1.2) * math.sin(math.radians(angle))
                skeleton = SkeletonEnemy(self.x + offset_x, self.y + offset_y)
                enemy_manager.add_enemy(skeleton)
            self.cooldown_timer = self.skeleton_cooldown
        else:
            self.cooldown_timer -= 1

    def update(self, player_x, player_y, enemy_manager, playable_area):
        """Update Arcanos' behavior."""
        self.move_relative_to_player(player_x, player_y, playable_area)
        self.spawn_skeletons(enemy_manager)

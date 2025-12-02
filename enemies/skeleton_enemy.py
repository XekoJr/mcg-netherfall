# enemies/bat_enemy.py

from enemies.enemy import Enemy
import pygame

class SkeletonEnemy(Enemy):
    """Basic flying bat enemy."""
    def __init__(self, x, y):
        # Load images specific to BatEnemy
        images = [
            pygame.image.load(f'./assets/images/enemies/skeleton/{i}.png') for i in range(4)
        ]
        super().__init__(x, y, hp=10, speed=3, xp_value=10, damage=25, size=(50, 50), images=images)

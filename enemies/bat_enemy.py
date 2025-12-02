from enemies.enemy import Enemy
import pygame

class BatEnemy(Enemy):
    """Basic flying bat enemy."""
    def __init__(self, x, y):
        # Load images specific to BatEnemy
        images = [
            pygame.image.load(f'./assets/images/enemies/bat/{i}.png') for i in range(4)
        ]
        super().__init__(x, y, hp=15, speed=1.5, xp_value=5, damage=10, size=(50, 35), images=images)

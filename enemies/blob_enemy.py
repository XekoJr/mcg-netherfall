from enemies.enemy import Enemy
import pygame

class BlobEnemy(Enemy):
    """Slow but high-health tank enemy."""
    def __init__(self, x, y):
        # Load images specific to TankEnemy
        images = [
            pygame.image.load(f'./assets/images/enemies/blob/{i}.png') for i in range(4)
        ]
        super().__init__(x, y, hp=50, speed=0.8, xp_value=20, damage=20, size=(80, 70), images=images)
        self.poison_damage = 3  # Damage per tick
        self.poison_duration = 10  # Poison lasts x seconds
        self.poison_tick_interval = 2  # Damage every x seconds

    def apply_poison(self, player):
        """Apply poison to the player if a collision occurs."""
        player.apply_status(
            "poison",
            self.poison_duration,
            self.poison_tick_interval,
            self.poison_damage,
            "Blob"
        )
import pygame
import time

from abilities.ability import Ability

class HealingAbility(Ability):
    """Slowly heals the player over time."""
    def __init__(self, name="Healing Aura", 
                 description="Heal 5 HP every 10 seconds", 
                 cost=5, 
                 icon_path='./assets/images/abilities/heal.png', 
                 images=[]
                 ):
        super().__init__(name, description, cost, icon_path, images, active=False)
        self.heal_amount = 5  # HP per heal
        self.cooldown = 10  # Seconds between heals
        self.last_heal_time = 0  # Tracks when we last healed

    def heal(self, player):
        """Heal the player if cooldown is ready."""
        current_time = time.time()
        if current_time - self.last_heal_time >= self.cooldown:
            if player.health < player.max_health:
                player.health += self.heal_amount
                player.health = min(player.health, player.max_health)  # Don't overheal
                self.last_heal_time = current_time

    def update(self, player):
        """Check if it's time to heal."""
        if not self.active:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_heal_time >= self.heal_interval:
            if player.health < player.max_health:
                player.health = min(player.health + self.heal_amount, player.max_health)
                self.last_heal_time = current_time

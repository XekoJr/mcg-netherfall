import time
from abilities.ability import Ability

class BurningAbility(Ability):
    """Sets enemies on fire when hit. Fire deals damage over time."""
    def __init__(self, name="Burning Touch",
                 description="Apply burning to enemies, dealing damage over time.",
                 cost=5,
                 icon_path='./assets/images/abilities/burn.png',
                 images=[]
                 ):
        super().__init__(name, description, cost, icon_path, images, active=False)
        self.base_burn_damage = 0.8
        self.base_burn_duration = 3  # How long it burns (seconds)
        self.burn_interval = 0.5  # Damage tick rate (seconds)
        self.burn_damage = self.base_burn_damage
        self.burn_duration = self.base_burn_duration

    def apply_burn(self, enemy):
        """Set an enemy on fire."""
        current_time = time.time()
        if not hasattr(enemy, "burn_end_time") or current_time > enemy.burn_end_time:
            enemy.burn_end_time = current_time + self.burn_duration
            enemy.next_burn_tick = current_time

    def update_burn(self, enemy):
        """Deal burn damage at regular intervals."""
        current_time = time.time()
        if hasattr(enemy, "burn_end_time") and current_time <= enemy.burn_end_time:
            if current_time >= enemy.next_burn_tick:
                enemy.take_damage(self.burn_damage)
                enemy.next_burn_tick += self.burn_interval

                # Check if the enemy is dead
                if enemy.hp <= 0:
                    return True  # Indicate the enemy is dead
        elif hasattr(enemy, "burn_end_time") and current_time > enemy.burn_end_time:
            del enemy.burn_end_time
            del enemy.next_burn_tick
        return False

    def update_attributes(self, burn_damage_level, burn_duration_level):
        """Upgrade burn stats based on skill levels."""
        self.burn_damage = self.base_burn_damage + (0.5 * burn_damage_level)
        self.burn_duration = self.base_burn_duration + (1 * burn_duration_level)

import pygame
import time
from abilities.ability import Ability

class ShieldAbility(Ability):
    """Blocks one hit, then goes on cooldown."""
    def __init__(self, name="Block Shield", 
                 description="Block one incoming attack and resets after 30 seconds.", 
                 cost=5, 
                 icon_path='assets/images/abilities/shield.png', 
                 images=[]
                 ):
        super().__init__(name, description, cost, icon_path, images, active=False)
        self.cooldown = 30  # Seconds before shield comes back
        self.blocked = False  # Did we just block something?
        self.last_block_time = None  # When did we last block?
        self.ready = True  # Is the shield ready to use?

    def block(self):
        """Block an attack and start cooldown."""
        if self.ready and self.active:
            self.blocked = True
            self.ready = False
            self.last_block_time = time.time()

    def update(self):
        """Check if cooldown is done and reset the shield."""
        if not self.ready:
            current_time = time.time()
            if self.last_block_time is not None:
                elapsed_time = current_time - self.last_block_time
                if elapsed_time >= self.cooldown:
                    self.reset_block()

    def reset_block(self):
        """Make the shield usable again."""
        self.blocked = False
        self.last_block_time = None
        self.ready = True

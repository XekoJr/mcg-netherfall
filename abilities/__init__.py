"""
Player abilities system.

Includes passive and active abilities that can be unlocked during gameplay.
"""

from .ability import Ability
from .burning_ability import BurningAbility
from .healing_ability import HealingAbility
from .invincibility_alibity import InvincibilityAbility
from .poison_ability import PoisonAbility
from .shield_ability import ShieldAbility

__all__ = [
    'Ability',
    'BurningAbility',
    'HealingAbility',
    'InvincibilityAbility',
    'PoisonAbility',
    'ShieldAbility'
]
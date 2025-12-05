"""
Powerups Classes

This module contains all powerup classes used in the game.
"""

from powerups.powerup import Powerup
from powerups.magnet_powerup import MagnetPowerup
from powerups.bomb_powerup import BombPowerup
from powerups.speed_powerup import SpeedPowerup
from powerups.rage_powerup import RagePowerup
from powerups.heal_powerup import HealPowerup

__all__ = [
    'Powerup',
    'MagnetPowerup',
    'BombPowerup',
    'SpeedPowerup',
    'RagePowerup',
    'HealPowerup'
]
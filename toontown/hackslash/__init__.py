"""Real-time rubber-hose melee combat foundation (KH x Toontown).

This package is the destination combat loop — not turn-based cog battles.
Slice 1: melee swing, short combo window, soft nearest-hostile targeting.
"""

from .MeleeCombat import MeleeCombatController
from .SoftTarget import SoftTargetFinder, HackSlashTarget
from .DemoHostile import DemoHostile

__all__ = [
    'MeleeCombatController',
    'SoftTargetFinder',
    'HackSlashTarget',
    'DemoHostile',
]

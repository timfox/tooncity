"""Real-time rubber-hose Oswald stretch-punch melee foundation.

This package is the destination combat loop — not turn-based cog battles.
Slice 1: stretch punches, short combo window, soft nearest-hostile targeting.
"""

from .MeleeCombat import MeleeCombatController
from .SoftTarget import SoftTargetFinder, HackSlashTarget
from .DemoHostile import DemoHostile
from . import HitJuice
from .DodgePerfectFx import DodgePerfectFx
from .DodgeTrailFx import DodgeTrailFx

__all__ = [
    'MeleeCombatController',
    'SoftTargetFinder',
    'HackSlashTarget',
    'DemoHostile',
    'HitJuice',
    'DodgePerfectFx',
    'DodgeTrailFx',
]

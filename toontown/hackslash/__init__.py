"""Real-time rubber-hose Oswald stretch-punch melee foundation.

This package is the destination combat loop — not turn-based cog battles.
Slice 1: stretch punches, short combo window, soft nearest-hostile targeting.
"""

from .MeleeCombat import MeleeCombatController
from .HackSlashConfig import (
    finisherFovPunchKeys,
    hurtStaggerTotalSec,
    isHurtRecoveryCancelWindowOpen,
    isJuggleCancelWindowOpen,
    isPerfectDodgeCounterWindowOpen,
    juggleCancelSlamHitIndex,
    perfectDodgeCounterOpenerDamage,
    perfectDodgeCounterOpenerRate,
)
from .SoftTarget import (
    SoftTargetFinder,
    HackSlashTarget,
    assistAimYawNudge,
    nextCycleIndex,
    pickCycleChoice,
    shouldAssistAimOnHit,
    signedYawDeltaDeg,
)
from .DemoHostile import DemoHostile
from . import HitJuice
from .DodgePerfectFx import DodgePerfectFx
from .DodgeTrailFx import DodgeTrailFx
from .DodgeIFrameCreamWashFx import DodgeIFrameCreamWashPulse
from .DodgeTrailCreamWashFx import DodgeTrailCreamWashPulse
from .ComboCounterCreamWashFx import ComboCounterCreamWashPulse
from .CreamHangCreamWashFx import CreamHangCreamWashPulse
from .CreamHangSparkleFx import CreamHangSparkleFx
from .CreamSlamFlashFx import CreamSlamFlashFx
from .FinisherCreamWashFx import FinisherCreamWashPulse
from .HitSparkFx import HitSparkFx
from .HitSparkCreamWashFx import HitSparkCreamWashPulse
from .HitStopFx import HitStopFx
from .PerfectDodgeCreamWashFx import PerfectDodgeCreamWashPulse
from .SlamDustFx import SlamDustFx
from .SoftLockCreamWashFx import SoftLockCreamWashPulse
from .SoftLockFovCreamWashFx import SoftLockFovCreamWashPulse
from .SoftLockReticleFx import SoftLockReticleFx

__all__ = [
    'MeleeCombatController',
    'finisherFovPunchKeys',
    'hurtStaggerTotalSec',
    'isHurtRecoveryCancelWindowOpen',
    'isJuggleCancelWindowOpen',
    'isPerfectDodgeCounterWindowOpen',
    'juggleCancelSlamHitIndex',
    'perfectDodgeCounterOpenerDamage',
    'perfectDodgeCounterOpenerRate',
    'SoftTargetFinder',
    'HackSlashTarget',
    'assistAimYawNudge',
    'nextCycleIndex',
    'pickCycleChoice',
    'shouldAssistAimOnHit',
    'signedYawDeltaDeg',
    'DemoHostile',
    'HitJuice',
    'ComboCounterCreamWashPulse',
    'CreamHangCreamWashPulse',
    'CreamHangSparkleFx',
    'CreamSlamFlashFx',
    'DodgePerfectFx',
    'DodgeTrailFx',
    'DodgeIFrameCreamWashPulse',
    'DodgeTrailCreamWashPulse',
    'FinisherCreamWashPulse',
    'HitSparkFx',
    'HitSparkCreamWashPulse',
    'HitStopFx',
    'PerfectDodgeCreamWashPulse',
    'SlamDustFx',
    'SoftLockCreamWashPulse',
    'SoftLockFovCreamWashPulse',
    'SoftLockReticleFx',
]

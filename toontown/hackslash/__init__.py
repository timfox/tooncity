"""Real-time rubber-hose Oswald stretch-punch melee foundation.

This package is the destination combat loop — not turn-based cog battles.
Slice 1: stretch punches, short combo window, soft nearest-hostile targeting.
"""

from .MeleeCombat import MeleeCombatController
from .HackSlashConfig import (
    comboCounterCreamEdgeAftershockAtSec,
    comboCounterCreamEdgePeakAtSec,
    dodgeCancelCreamWashAftershockAtSec,
    dodgeCancelCreamWashPeakAtSec,
    dodgeIFrameCreamWashPeakAtSec,
    finisherFovPunchKeys,
    hitAssistCreamWashAftershockAtSec,
    hitAssistCreamWashPeakAtSec,
    hurtStaggerCreamWashAftershockAtSec,
    hurtStaggerCreamWashPeakAtSec,
    hurtStaggerTotalSec,
    isHurtRecoveryCancelWindowOpen,
    isJuggleCancelWindowOpen,
    isJuggleHangStunHit,
    isJuggleHangStunned,
    isPerfectDodgeCounterWindowOpen,
    juggleCancelSlamHitIndex,
    juggleHangStunSec,
    acceptMeleeHitIndex,
    comboDamageTableFromReclaimCount,
    earnedCounterUntil,
    expectedMeleeComboHitIndex,
    isMeleeHitCadenceReady,
    meleeDamageFromHitIndex,
    meleeHitPlanarRange,
    perfectDodgeCounterOpenerDamage,
    perfectDodgeCounterOpenerRate,
    powerBumpMultiplier,
    remapMeleeComboIndexOnSoftLockChange,
    resolveEarnedCounterFlags,
    softLockCycleCreamWashPeakAtSec,
    softLockCyclePulseScaleKeys,
)
from .SoftTarget import (
    SoftTargetFinder,
    HackSlashTarget,
    assistAimYawNudge,
    nextCycleIndex,
    pickCycleChoice,
    pickSoftLockAcquire,
    shouldAssistAimOnHit,
    shouldCyclePreferPriority,
    shouldStickyYieldToPriority,
    signedYawDeltaDeg,
    softLockAcquireRank,
)
from .DemoHostile import DemoHostile
from . import HitJuice
from .DodgeCancelCreamWashFx import DodgeCancelCreamWashPulse
from .DodgePerfectFx import DodgePerfectFx
from .DodgeTrailFx import DodgeTrailFx
from .DodgeIFrameCreamWashFx import DodgeIFrameCreamWashPulse
from .DodgeTrailCreamWashFx import DodgeTrailCreamWashPulse
from .ComboCounterCreamEdgeFx import ComboCounterCreamEdgePulse
from .ComboCounterCreamWashFx import ComboCounterCreamWashPulse
from .CreamHangCreamWashFx import CreamHangCreamWashPulse
from .CreamHangSparkleFx import CreamHangSparkleFx
from .CreamSlamFlashFx import CreamSlamFlashFx
from .FinisherCreamWashFx import FinisherCreamWashPulse
from .HitAssistCreamWashFx import HitAssistCreamWashPulse
from .HitSparkFx import HitSparkFx
from .HitSparkCreamWashFx import HitSparkCreamWashPulse
from .HitStopFx import HitStopFx
from .HurtStaggerCreamWashFx import HurtStaggerCreamWashPulse
from .PerfectDodgeCreamWashFx import PerfectDodgeCreamWashPulse
from .SlamDustFx import SlamDustFx
from .SoftLockCreamWashFx import SoftLockCreamWashPulse
from .SoftLockCycleCreamWashFx import SoftLockCycleCreamWashPulse
from .SoftLockFovCreamWashFx import SoftLockFovCreamWashPulse
from .SoftLockReticleFx import SoftLockReticleFx

__all__ = [
    'MeleeCombatController',
    'comboCounterCreamEdgeAftershockAtSec',
    'comboCounterCreamEdgePeakAtSec',
    'dodgeCancelCreamWashAftershockAtSec',
    'dodgeCancelCreamWashPeakAtSec',
    'dodgeIFrameCreamWashPeakAtSec',
    'finisherFovPunchKeys',
    'hitAssistCreamWashAftershockAtSec',
    'hitAssistCreamWashPeakAtSec',
    'hurtStaggerCreamWashAftershockAtSec',
    'hurtStaggerCreamWashPeakAtSec',
    'hurtStaggerTotalSec',
    'isHurtRecoveryCancelWindowOpen',
    'isJuggleCancelWindowOpen',
    'isJuggleHangStunHit',
    'isJuggleHangStunned',
    'isPerfectDodgeCounterWindowOpen',
    'juggleCancelSlamHitIndex',
    'juggleHangStunSec',
    'acceptMeleeHitIndex',
    'comboDamageTableFromReclaimCount',
    'earnedCounterUntil',
    'expectedMeleeComboHitIndex',
    'isMeleeHitCadenceReady',
    'meleeDamageFromHitIndex',
    'meleeHitPlanarRange',
    'perfectDodgeCounterOpenerDamage',
    'perfectDodgeCounterOpenerRate',
    'powerBumpMultiplier',
    'remapMeleeComboIndexOnSoftLockChange',
    'resolveEarnedCounterFlags',
    'softLockCycleCreamWashPeakAtSec',
    'softLockCyclePulseScaleKeys',
    'SoftTargetFinder',
    'HackSlashTarget',
    'assistAimYawNudge',
    'nextCycleIndex',
    'pickCycleChoice',
    'pickSoftLockAcquire',
    'shouldAssistAimOnHit',
    'shouldCyclePreferPriority',
    'shouldStickyYieldToPriority',
    'signedYawDeltaDeg',
    'softLockAcquireRank',
    'DemoHostile',
    'HitJuice',
    'ComboCounterCreamEdgePulse',
    'ComboCounterCreamWashPulse',
    'CreamHangCreamWashPulse',
    'CreamHangSparkleFx',
    'CreamSlamFlashFx',
    'DodgeCancelCreamWashPulse',
    'DodgePerfectFx',
    'DodgeTrailFx',
    'DodgeIFrameCreamWashPulse',
    'DodgeTrailCreamWashPulse',
    'FinisherCreamWashPulse',
    'HitAssistCreamWashPulse',
    'HitSparkFx',
    'HitSparkCreamWashPulse',
    'HitStopFx',
    'HurtStaggerCreamWashPulse',
    'PerfectDodgeCreamWashPulse',
    'SlamDustFx',
    'SoftLockCreamWashPulse',
    'SoftLockCycleCreamWashPulse',
    'SoftLockFovCreamWashPulse',
    'SoftLockReticleFx',
]

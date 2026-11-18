"""Rubber-hose cream wash pulse after soft-lock cycle reticle cream ring.

Fullscreen soft cream veil that settles *after* SoftLockReticleFx Tab/`
cycle cream pulse ring (#210 deepen) — SoftLockCreamWashPulse (#155) /
SoftLockFovCreamWashPulse (#160) overlay grammar as a brief cycle settle
beat so target switching reads juicier. Quieter/faster under acquire
reticle wash (#155); cream / pastel only (not ink). Distinct from dodge
i-frame cream wash deepen (#228) and acquire reticle pulse (#92). Wired
from SoftLockReticleFx.playCyclePulse beside the deepened cycle cream
ring. Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from . import HackSlashConfig


class SoftLockCycleCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after Tab/` cycle cream ring."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_PEAK', 0.06))
        mid = float(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_MID', 0.035))
        inSec = float(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_IN_SEC', 0.04))
        pulseSec = float(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_PULSE_SEC', 0.06))
        holdSec = float(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_HOLD_SEC', 0.03))
        outSec = float(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_OUT_SEC', 0.18))
        binSort = int(getattr(
            HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_BIN', 27))
        if delay is None:
            delay = float(getattr(
                HackSlashConfig, 'SOFT_LOCK_CYCLE_CREAM_WASH_DELAY_SEC', 0.12))

        try:
            cm = CardMaker('hackslash-softlock-cycle-cream-wash')
            # Full-frame veil — quieter/faster than acquire reticle wash.
            cm.setFrame(-2, 2, -2, 2)
            wash = parent.attachNewNode(cm.generate())
            wash.setTransparency(TransparencyAttrib.MAlpha)
            wash.setColor(r, g, b, 1)
            wash.setColorScale(r, g, b, 0)
            wash.setBin('fixed', binSort)
            wash.setDepthTest(False)
            wash.setDepthWrite(False)
            self._washNP = wash
        except Exception:
            self._washNP = None
            return None

        # Delayed two-beat after cycle cream ring: bright → settle → fade.
        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            LerpColorScaleInterval(
                wash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            LerpColorScaleInterval(
                wash, max(0.01, pulseSec), Vec4(r, g, b, mid),
                blendType='easeInOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                wash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
            Func(self.clear),
            name='hackslashSoftLockCycleCreamWash',
        )
        self._ival.start()
        return self._ival

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._washNP
        self._washNP = None
        if wash is None:
            return
        try:
            if not wash.isEmpty():
                wash.removeNode()
        except Exception:
            pass

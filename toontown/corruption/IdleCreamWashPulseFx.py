"""Rubber-hose cream wash pulse on corrupt idle cream drip / sparkle stack.

Fullscreen soft cream veil that pulses between telegraphs — DeathCreamWashPulse
(#119) / HitSparkCreamWashPulse (#134) overlay grammar as a brief ambient
settle beat against ink idle drips. Soft under world-space IdleInkDrip +
IdleCreamDripContrast + IdleCreamDripSparkle; cream / pastel only (not ink).
Wired from DistributedCorruptToon beside IdleInkDrip + IdleCreamDrip +
IdleCreamDripSparkle (start / pause / resume / clear together). Client only.
Toontown spiritual sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def idleCreamWashLook(archetype=None, finaleLook=None):
    """Resolve idle cream-wash tunables; compose period with drip sparkle look."""
    look = dict(getattr(
        CorruptionGlobals, 'IDLE_CREAM_WASH_LOOK', {}) or {})
    # Lazy import avoids circular load with IdleCreamDripSparkleFx.
    try:
        from toontown.corruption.IdleCreamDripSparkleFx import (
            idleCreamDripSparkleLook)
        sparkle = idleCreamDripSparkleLook(archetype, finaleLook=finaleLook)
        sparklePeriod = float(sparkle.get('periodSec', 1.48))
        # Slower than drip sparkles so wash reads as soft ambient settle,
        # not sync-locked with fleck twinkles.
        look.setdefault(
            'periodSec',
            sparklePeriod * float(look.get('periodScale', 2.15)))
        look.setdefault(
            'settleSec',
            float(sparkle.get('settleSec', 0.55)) + float(
                look.get('settleBias', 0.48)))
    except Exception:
        look.setdefault('periodSec', 3.2)
        look.setdefault('settleSec', 1.05)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_BIN', 36)))
    return look


class IdleCreamWashPulse(object):
    """Owns looping soft aspect2d cream wash pulses during corrupt idle."""

    def __init__(self):
        self._loopIval = None
        self._pulseIval = None
        self._washNP = None
        self._paused = False
        self._parent = None
        self._archetype = CorruptionGlobals.ARCHETYPE_INK
        self._finaleLook = None
        self._look = None

    def start(self, parent, archetype=None, finaleLook=None):
        """Begin sparse looping cream wash pulses. Returns loop or None.

        `parent` is accepted for parity with idle drip / sparkle start
        signatures (wash itself is aspect2d); kept so callers share one
        start(parent, archetype, finaleLook) pattern.
        """
        self.clear()
        if not getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_ENABLED', True):
            return None
        if parent is None:
            return None
        try:
            if parent.isEmpty():
                return None
        except Exception:
            return None
        self._parent = parent
        self._archetype = archetype
        self._finaleLook = finaleLook
        self._look = idleCreamWashLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(1.1, float(self._look.get('periodSec', 3.2)))
        settle = max(0.15, float(self._look.get('settleSec', 1.05)))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitPulse),
            Wait(period),
            name='corruptIdleCreamWashLoop',
        )
        self._loopIval.loop()
        return self._loopIval

    def pause(self):
        """Stop emitting + clear wash so telegraph / hit juice owns the frame."""
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
        self._clearPulse()

    def resume(self):
        """Resume idle cream wash after telegraph / hit recovery."""
        if not getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_ENABLED', True):
            return
        if self._parent is None:
            return
        try:
            if self._parent.isEmpty():
                return
        except Exception:
            return
        self._paused = False
        if self._loopIval is not None:
            try:
                self._loopIval.resume()
                return
            except Exception:
                pass
        self.start(
            self._parent,
            archetype=self._archetype,
            finaleLook=self._finaleLook,
        )

    def clear(self):
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
            self._loopIval = None
        self._clearPulse()
        self._parent = None
        self._look = None

    def _clearPulse(self):
        if self._pulseIval is not None:
            try:
                self._pulseIval.pause()
            except Exception:
                pass
            self._pulseIval = None
        wash = self._washNP
        self._washNP = None
        if wash is None:
            return
        try:
            if not wash.isEmpty():
                wash.removeNode()
        except Exception:
            pass

    def _emitPulse(self):
        """One soft two-beat cream wash — death / melee wash vocabulary."""
        if self._paused or self._look is None:
            return
        self._clearPulse()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        cream = getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = self._look.get('color') or (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(self._look.get(
            'peak',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_PEAK', 0.055)))
        mid = float(self._look.get(
            'mid',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_MID', 0.032)))
        inSec = float(self._look.get(
            'inSec',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_IN_SEC', 0.07)))
        pulseSec = float(self._look.get(
            'pulseSec',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_PULSE_SEC', 0.12)))
        holdSec = float(self._look.get(
            'holdSec',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_HOLD_SEC', 0.10)))
        outSec = float(self._look.get(
            'outSec',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_OUT_SEC', 0.48)))
        binSort = int(self._look.get(
            'binSort',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_BIN', 36)))
        delay = float(self._look.get(
            'delaySec',
            getattr(CorruptionGlobals, 'IDLE_CREAM_WASH_DELAY_SEC', 0.0)))

        try:
            cm = CardMaker('corrupt-idle-cream-wash')
            # Full-frame veil — death / melee / reclaim cream wash grammar.
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
            return

        # Soft two-beat ambient pulse: bright → settle → fade (quieter than
        # death #119 / melee hit #134 — idle contrast against ink drips).
        self._pulseIval = Sequence(
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
            Func(self._clearPulse),
            name='corruptIdleCreamWashPulse',
        )
        self._pulseIval.start()

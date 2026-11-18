"""Rubber-hose cream wash pulse after CorruptDeathCreamFleckFx.

Fullscreen soft cream veil that settles *after* the sunny death fleck burst —
PurityCompleteCreamWashFx / EntryCreamWashPulseFx overlay grammar as a brief
defeat aftershock. Soft under world-space flecks; cream / pastel only (not
ink). Wired from DeathPopSplat.play beside DeathCreamFleckBurst. Client only.
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


class DeathCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after death cream flecks."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(CorruptionGlobals, 'DEATH_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(CorruptionGlobals, 'DEATH_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_PEAK', 0.14))
        mid = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_MID', 0.08))
        inSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_IN_SEC', 0.06))
        pulseSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_PULSE_SEC', 0.10))
        holdSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_HOLD_SEC', 0.08))
        outSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_OUT_SEC', 0.42))
        binSort = int(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_BIN', 38))
        if delay is None:
            delay = float(getattr(
                CorruptionGlobals, 'DEATH_CREAM_WASH_DELAY_SEC', 0.20))

        try:
            cm = CardMaker('corrupt-death-cream-wash')
            # Full-frame veil — reclaim purity / entry cream wash grammar.
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

        # Delayed two-beat after fleck burst: bright pop → soft settle → fade.
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
            name='corruptDeathCreamWash',
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

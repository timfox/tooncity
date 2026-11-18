"""Rubber-hose cream wash pulse after reclaim purity-fill cream aftershock.

Fullscreen soft cream veil that settles *after* PurityMeterHud fill cream
aftershock (#123) / fill shimmer (#90) — CheerCreamWashPulse /
WaveClearCreamWashPulse / PurityCompleteCreamWashFx overlay grammar as a brief
purity-fill settle beat. Soft under meter flecks; cream / pastel only (not
ink). Wired from PurityMeterHud._spawnFillShimmerFlecks beside the cream
aftershock. Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.reclaim import ReclaimGlobals


class PurityFillCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after purity-fill cream aftershock."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_PEAK', 0.09))
        mid = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_MID', 0.045))
        inSec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_IN_SEC', 0.05))
        pulseSec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_PULSE_SEC', 0.09))
        holdSec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_HOLD_SEC', 0.06))
        outSec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_OUT_SEC', 0.34))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_BIN', 48))
        if delay is None:
            delay = float(getattr(
                ReclaimGlobals, 'PURITY_METER_FILL_CREAM_WASH_DELAY_SEC', 0.40))

        try:
            cm = CardMaker('reclaim-purity-fill-cream-wash')
            # Full-frame veil — cheer / wave-clear / entry / purity grammar.
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

        # Delayed two-beat after cream aftershock: bright → settle → fade.
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
            name='reclaimPurityFillCreamWash',
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

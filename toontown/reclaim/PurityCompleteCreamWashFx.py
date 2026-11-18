"""Rubber-hose cream wash pulse when reclaim hits full purity.

Fullscreen soft cream veil that pops on purityRestoreFx — StreetColorWash
overlay grammar as a discrete payoff beat, layered under StreetSparkleFx
horizon glitter. Sibling of EntryCreamWashPulseFx (softer entry beat with
EntryCreamShimmerFx). Does not restage progressive wash geom tint, purity
FOV / rays, cheer flecks, or wave-clear cream. Toontown spiritual-sequel
tone only — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class PurityCompleteCreamWashFxClient(DirectObject):
    """Listens for purity restore and plays a cream wash pulse veil."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._washNP = None
        self.accept('purityRestoreFx', self._onPurityRestore)
        self.accept('purityRestoreSettled', self._onSettled)

    def destroy(self):
        self.ignoreAll()
        self.clear()

    def _onPurityRestore(self, zoneId=None):
        self.playPulse()

    def _onSettled(self, zoneId=None):
        self.clear()

    def playPulse(self):
        """Two-beat cream wash pulse (bright pop → soft settle → fade)."""
        if not getattr(
                ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        cream = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = getattr(
                ReclaimGlobals, 'STREET_WASH_CREAM', (1.0, 0.97, 0.82))
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_PEAK', 0.28))
        mid = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_MID', 0.16))
        inSec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_OUT_SEC', 0.55))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_WASH_BIN', 40))

        try:
            cm = CardMaker('reclaim-purity-complete-cream-wash')
            # Full-frame veil — StreetColorWash overlay grammar, not horizon.
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

        # Rubber-hose two-beat: bright pop → soft settle pulse → fade under
        # StreetSparkleFx horizon glitter (bin 50) and purity burst flash.
        self._ival = Sequence(
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
            name='reclaimPurityCompleteCreamWash',
        )
        self._ival.start()

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


_client = None


def ensurePurityCompleteCreamWashFxClient():
    global _client
    if _client is None:
        _client = PurityCompleteCreamWashFxClient()
    return _client

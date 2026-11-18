"""Rubber-hose cream wash pulse when reclaim hits full purity.

Fullscreen soft cream veil that pops on purityRestoreFx — StreetColorWash
overlay grammar as a discrete payoff beat, layered under StreetSparkleFx
horizon glitter. Sibling of EntryCreamWashPulseFx (softer entry beat with
EntryCreamShimmerFx). A delayed cream aftershock (softer flecks settling
downward + soft halo) follows the wash pulse — same residual grammar as
entry cream wash aftershock (#132), wave-clear cream aftershock (#127), and
purity-fill cream aftershock (#123). Does not restage progressive wash geom
tint, purity FOV / rays / FOV cream wash, cheer flecks, or wave-clear cream.
Toontown spiritual-sequel tone only — no keyblades / no KH branding.
"""

from math import cos, pi

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class PurityCompleteCreamWashFxClient(DirectObject):
    """Listens for purity restore; owns cream wash pulse + delayed aftershock."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._washPlayIval = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None
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
        """Two-beat cream wash pulse (bright pop → soft settle → fade) + aftershock."""
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
        washIval = Sequence(
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
            name='reclaimPurityCompleteCreamWashVeil',
        )
        self._washPlayIval = washIval
        try:
            washIval.start()
        except Exception:
            self.clear()
            return

        washLifetime = inSec + pulseSec + holdSec + outSec
        origin = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_ORIGIN',
            (0.0, 0.0, -0.06))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.06

        aftershock = self._buildAftershock(parent, ox, oy, oz)
        if aftershock is not None:
            # Wash Sequence already started; hold its lifetime beside aftershock.
            self._ival = Sequence(
                Parallel(
                    Wait(washLifetime + 0.04),
                    aftershock,
                ),
                Func(self.clear),
                name='reclaimPurityCompleteCreamWash',
            )
        else:
            self._ival = Sequence(
                Wait(washLifetime + 0.04),
                Func(self.clear),
                name='reclaimPurityCompleteCreamWash',
            )
        self._ival.start()

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after purity-complete wash."""
        if not getattr(
                ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_DELAY_SEC', 0.20))
        parts = []

        if getattr(
                ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_ENABLED',
                True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_SEC', 0.34))
        for i in range(count):
            part = self._spawnAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_HALF', 0.50))
        startScale = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_START', 0.28))
        peakScale = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_PEAK', 1.18))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_SEC', 0.28))
        peakA = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA',
            0.14))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_BIN', 42))
        try:
            cm = CardMaker('reclaim-purity-complete-cream-aftershock-halo')
            # Soft oval halo under StreetSparkleFx — quieter residual of wash.
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parent.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(ox, oy, oz)
            halo.setScale(startScale)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
        except Exception:
            return None
        self._haloNP = halo
        return Parallel(
            LerpScaleInterval(
                halo, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.2)),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.8), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_SIZE', 0.016))
        drift = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_DRIFT', 0.30))
        fall = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_FALL', 0.24))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.80))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_CREAM_AFTERSHOCK_BIN', 42))
        angle = (2.0 * pi * index) / float(count) + 0.31
        try:
            cm = CardMaker(
                'reclaim-purity-complete-cream-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the cream wash.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.08
            startZ = oz + 0.014 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream, not StreetSparkleFx's outward rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.04 * (index % 3))
        peak = 1.05 + 0.08 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.28), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.72), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.72), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def clear(self):
        """Stop wash/aftershock and remove every cream purity-complete node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._washPlayIval is not None:
            try:
                self._washPlayIval.pause()
            except Exception:
                pass
            self._washPlayIval = None
        wash = self._washNP
        self._washNP = None
        if wash is not None and not wash.isEmpty():
            try:
                wash.removeNode()
            except Exception:
                pass
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._fleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []


_client = None


def ensurePurityCompleteCreamWashFxClient():
    global _client
    if _client is None:
        _client = PurityCompleteCreamWashFxClient()
    return _client

"""Rubber-hose street sparkle when reclaim hits full purity.

Cream glitter rises from the street horizon after wash clears — a hood-wide
payoff layered with StreetColorWash soft-clear, PurityCompleteCreamWashFx
cream pulse + delayed cream aftershock, PurityBurstFx FOV/rays, and the
lighter wave cream burst. Birds return stays on the corruption audio path
via the same purityRestoreFx messenger. Toontown spiritual-sequel tone only
— no keyblades / no KH branding.
"""

from math import cos, pi, sin

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


class StreetSparkleFxClient(DirectObject):
    """Listens for purity restore and plays street-horizon cream glitter."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._shimmerNP = None
        self._sparkleNPs = []
        self.accept('purityRestoreFx', self._onPurityRestore)
        self.accept('purityRestoreSettled', self._onSettled)

    def destroy(self):
        self.ignoreAll()
        self.clear()

    def _onPurityRestore(self, zoneId=None):
        self.playSparkle()

    def _onSettled(self, zoneId=None):
        self.clear()

    def playSparkle(self):
        """Horizon shimmer + rising cream sparkles (no FOV — purity owns that)."""
        if not getattr(ReclaimGlobals, 'STREET_SPARKLE_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'STREET_SPARKLE_ORIGIN', (0.0, 0.0, -0.42))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.42

        r, g, b, _a = getattr(
            ReclaimGlobals, 'STREET_SPARKLE_COLOR', (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(ReclaimGlobals, 'STREET_SPARKLE_BIN', 50))
        parts = []

        shimmerPart = self._spawnShimmer(parent, ox, oy, oz, r, g, b, binSort)
        if shimmerPart is not None:
            parts.append(shimmerPart)

        sparkleParts = self._spawnSparkles(parent, ox, oy, oz, binSort)
        parts.extend(sparkleParts)

        if not parts:
            return
        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='reclaimStreetSparkle',
        )
        self._ival.start()

    def _spawnShimmer(self, parent, ox, oy, oz, r, g, b, binSort):
        """Soft low-screen cream veil — reads as washed street glitter bed."""
        peak = float(getattr(ReclaimGlobals, 'STREET_SPARKLE_SHIMMER_PEAK', 0.22))
        inSec = float(getattr(
            ReclaimGlobals, 'STREET_SPARKLE_SHIMMER_IN_SEC', 0.08))
        holdSec = float(getattr(
            ReclaimGlobals, 'STREET_SPARKLE_SHIMMER_HOLD_SEC', 0.18))
        outSec = float(getattr(
            ReclaimGlobals, 'STREET_SPARKLE_SHIMMER_OUT_SEC', 0.55))
        try:
            cm = CardMaker('reclaim-street-sparkle-shimmer')
            # Wide low band — street plane, not a full-screen purity flash.
            cm.setFrame(-2.2, 2.2, -0.55, 0.35)
            shimmer = parent.attachNewNode(cm.generate())
            shimmer.setTransparency(TransparencyAttrib.MAlpha)
            shimmer.setColor(r, g, b, 1)
            shimmer.setColorScale(r, g, b, 0)
            shimmer.setPos(ox, oy, oz)
            shimmer.setBin('fixed', binSort)
            shimmer.setDepthTest(False)
            shimmer.setDepthWrite(False)
            self._shimmerNP = shimmer
        except Exception:
            self._shimmerNP = None
            return None
        return Sequence(
            LerpColorScaleInterval(
                shimmer, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                shimmer, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
        )

    def _spawnSparkles(self, parent, ox, oy, oz, binSort):
        count = int(getattr(ReclaimGlobals, 'STREET_SPARKLE_COUNT', 16))
        if count <= 0:
            return []
        size = float(getattr(ReclaimGlobals, 'STREET_SPARKLE_SIZE', 0.022))
        rise = float(getattr(ReclaimGlobals, 'STREET_SPARKLE_RISE', 0.72))
        spread = float(getattr(ReclaimGlobals, 'STREET_SPARKLE_SPREAD', 1.35))
        sec = float(getattr(ReclaimGlobals, 'STREET_SPARKLE_SEC', 0.62))
        r, g, b, a = getattr(
            ReclaimGlobals, 'STREET_SPARKLE_FLECK_COLOR',
            (1.0, 0.98, 0.72, 0.95))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'STREET_SPARKLE_FLECK_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))

        parts = []
        for i in range(count):
            try:
                # Fan across the street width; stagger depth so it reads ground-up.
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.35
                cm = CardMaker('reclaim-street-sparkle-%s' % i)
                # Alternate chip / cross fleck — rubber-hose cream glitter.
                if (i % 3) == 0:
                    cm.setFrame(-size * 0.35, size * 0.35, -size * 1.35, size * 1.35)
                elif (i % 3) == 1:
                    cm.setFrame(-size * 1.35, size * 1.35, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                sparkle = parent.attachNewNode(cm.generate())
                sparkle.setTransparency(TransparencyAttrib.MAlpha)
                sparkle.setColor(r, g, b, 1)
                sparkle.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.04
                startZ = oz + 0.02 * (i % 4) + sin(angle) * 0.02
                sparkle.setPos(startX, oy, startZ)
                sparkle.setScale(0.4 + 0.1 * (i % 4))
                sparkle.setBin('fixed', binSort + 1 + (i % 2))
                sparkle.setDepthTest(False)
                sparkle.setDepthWrite(False)
                self._sparkleNPs.append(sparkle)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.12,
                oy,
                startZ + rise * (0.55 + 0.45 * ((i % 5) / 4.0)))
            delay = 0.022 * i
            twinkle = 0.05 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        sparkle, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        sparkle, twinkle, 1.15, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        sparkle, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        sparkle, max(0.01, sec), 0.06, blendType='easeIn'),
                    LerpColorScaleInterval(
                        sparkle, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        shimmer = self._shimmerNP
        self._shimmerNP = None
        if shimmer is not None and not shimmer.isEmpty():
            try:
                shimmer.removeNode()
            except Exception:
                pass
        for np in self._sparkleNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._sparkleNPs = []


_client = None


def ensureStreetSparkleFxClient():
    global _client
    if _client is None:
        _client = StreetSparkleFxClient()
    return _client

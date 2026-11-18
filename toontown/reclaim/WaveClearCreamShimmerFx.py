"""Rubber-hose cream shimmer hang after reclaim wave-clear cream burst.

Soft aspect2d cream veil + rising flecks that fire *after* WaveCreamBurstFx
settles — residual sunny hang so the clear beat lingers without restaging the
flash/ring. Matches EntryCreamShimmer / StreetSparkle chip style. A delayed
cream aftershock (softer flecks settling downward + soft halo) follows the
hang — same residual grammar as purity-fill cream aftershock (#123) and cheer
cream aftershock (#118). Layers with cheer pitch swell and street wash; never
stomps full-purity FOV / StreetSparkle payoff. Toontown spiritual-sequel tone
only — no keyblades / no KH branding.
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


class WaveClearCreamShimmerFxClient(DirectObject):
    """Listens for wave clear; owns cream shimmer hang + delayed aftershock."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._shimmerPlayIval = None
        self._shimmerNP = None
        self._fleckNPs = []
        self._haloNP = None
        self.accept('reclaimWaveCleared', self._onWaveCleared)

    def destroy(self):
        self.ignoreAll()
        self.clear()

    def _onWaveCleared(self, zoneId=None, waveIndex=0):
        self.playHang()

    def playHang(self):
        """Soft cream veil + flecks after the wave-clear burst peak + aftershock."""
        if not getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_ORIGIN',
            (0.0, 0.0, 0.10))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.10

        r, g, b, _a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_BIN', 51))
        delay = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_DELAY_SEC', 0.28))

        parts = []
        shimmerPart = self._spawnShimmer(parent, ox, oy, oz, r, g, b, binSort)
        if shimmerPart is not None:
            parts.append(shimmerPart)
        fleckParts = self._spawnFlecks(parent, ox, oy, oz, binSort)
        parts.extend(fleckParts)
        if not parts:
            return

        # Hang starts after WaveCreamBurstFx flash/flecks settle.
        shimmerIval = Parallel(*parts, name='reclaimWaveClearCreamShimmerHang')
        self._shimmerPlayIval = shimmerIval

        # Lifetime hold matches the longer of veil / fleck hang.
        inSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_IN_SEC', 0.08))
        holdSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_HOLD_SEC', 0.34))
        outSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_OUT_SEC', 0.52))
        fleckSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_SEC', 0.55))
        hangSec = max(inSec + holdSec + outSec, fleckSec)

        aftershock = self._buildAftershock(parent, ox, oy, oz)

        def _kickHang():
            try:
                shimmerIval.start()
            except Exception:
                self.clear()

        if aftershock is not None:
            # Shimmer Parallel starts after hang delay; aftershock rides beside it.
            self._ival = Sequence(
                Wait(max(0.0, delay)),
                Func(_kickHang),
                Parallel(
                    Wait(hangSec + 0.04),
                    aftershock,
                ),
                Func(self.clear),
                name='reclaimWaveClearCreamShimmer',
            )
        else:
            self._ival = Sequence(
                Wait(max(0.0, delay)),
                Func(_kickHang),
                Wait(hangSec + 0.04),
                Func(self.clear),
                name='reclaimWaveClearCreamShimmer',
            )
        self._ival.start()

    def _spawnShimmer(self, parent, ox, oy, oz, r, g, b, binSort):
        """Soft mid-screen cream veil — residual hang, not a second flash."""
        peak = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_PEAK', 0.16))
        inSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_IN_SEC', 0.08))
        holdSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_HOLD_SEC', 0.34))
        outSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_OUT_SEC', 0.52))
        try:
            cm = CardMaker('reclaim-wave-clear-cream-shimmer')
            # Open center band — hang glitter bed, not full-screen purity flash.
            cm.setFrame(-1.55, 1.55, -0.62, 0.58)
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

    def _spawnFlecks(self, parent, ox, oy, oz, binSort):
        """Sunny cream chips that rise and hang — StreetSparkle / EntryCream."""
        count = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_COUNT', 10))
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_SIZE', 0.020))
        rise = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_RISE', 0.48))
        spread = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_SPREAD', 1.05))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_SEC', 0.55))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_COLOR',
            (1.0, 0.98, 0.72, 0.90))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SHIMMER_FLECK_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.31
                cm = CardMaker('reclaim-wave-clear-cream-shimmer-fleck-%s' % i)
                # Alternate chip / cross fleck — rubber-hose cream glitter.
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.30, size * 1.30)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.30, size * 1.30, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.035
                startZ = oz + 0.018 * (i % 3) + sin(angle) * 0.018
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.4 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort + 1 + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._fleckNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.10,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            delay = 0.020 * i
            twinkle = 0.05 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.10, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.06, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after wave-clear shimmer."""
        if not getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_DELAY_SEC', 0.24))
        parts = []

        if getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_SEC', 0.34))
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
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_HALF', 0.42))
        startScale = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_START', 0.28))
        peakScale = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_PEAK', 1.20))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_SEC', 0.28))
        peakA = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.14))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_BIN', 52))
        try:
            cm = CardMaker('reclaim-wave-clear-cream-aftershock-halo')
            # Soft oval halo under the hang band — quieter than cheer mid-screen.
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
        """Softer cream chip that settles downward — residual shimmer aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_SIZE', 0.016))
        drift = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_DRIFT', 0.32))
        fall = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_FALL', 0.26))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.82))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_AFTERSHOCK_BIN', 52))
        angle = (2.0 * pi * index) / float(count) + 0.35
        try:
            cm = CardMaker('reclaim-wave-clear-cream-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the shimmer glitter.
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

        # Settle downward — residual cream, not the shimmer's outward rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.05 * (index % 3))
        peak = 1.05 + 0.08 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.018 * (index % 3)
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
        """Stop shimmer/aftershock and remove every cream hang node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._shimmerPlayIval is not None:
            try:
                self._shimmerPlayIval.pause()
            except Exception:
                pass
            self._shimmerPlayIval = None
        shimmer = self._shimmerNP
        self._shimmerNP = None
        if shimmer is not None and not shimmer.isEmpty():
            try:
                shimmer.removeNode()
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


def ensureWaveClearCreamShimmerFxClient():
    global _client
    if _client is None:
        _client = WaveClearCreamShimmerFxClient()
    return _client

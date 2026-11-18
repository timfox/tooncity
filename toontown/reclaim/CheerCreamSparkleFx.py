"""Rubber-hose cream sparkle flecks layered on reclaim cheer pitch swell.

Short aspect2d cream chips that pop with ReclaimCheer SFX playRate ramp —
visual twin of the audio swell on wave clear / purity restore. Matches
StreetSparkle / EntryCreamShimmer chip style (cream/pastel only). A delayed
cream aftershock (softer flecks settling downward + soft halo) follows the
sparkle — same residual grammar as hang / perfect-dodge cream aftershock.
Does not restage WaveCreamBurst flash/ring, WaveClearCreamShimmer hang,
StreetSparkle horizon glitter, or purity FOV. Toontown spiritual-sequel
tone only — no keyblades / no KH branding.
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


class CheerCreamSparkleFxClient(DirectObject):
    """Listens for cheer messengers; owns cream flecks + delayed aftershock."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._sparkleIval = None
        self._fleckNPs = []
        self._haloNP = None
        self._lastSparkleT = -1.0
        # Same messengers as ReclaimCheer — layer flecks on the pitch swell.
        self.accept('npcCheerStub', self._onPurityCheer)
        self.accept('purityRestoreFx', self._onPurityCheer)
        self.accept('reclaimWaveCleared', self._onWaveCleared)
        self.accept('purityRestoreSettled', self._onSettled)

    def destroy(self):
        self.ignoreAll()
        self.clear()

    def _onPurityCheer(self, zoneId=None):
        if self._debounce():
            return
        self.playSparkle(full=True)

    def _onWaveCleared(self, zoneId=None, waveIndex=0):
        if self._debounce(minGap=0.2):
            return
        # Quieter cousin — fewer / shorter flecks than full purity cheer.
        self.playSparkle(full=False)

    def _onSettled(self, zoneId=None):
        self.clear()

    def _debounce(self, minGap=0.35):
        """Match ReclaimCheer debounce so duplicate purity stubs don't double."""
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            return False
        if now - self._lastSparkleT < float(minGap):
            return True
        self._lastSparkleT = now
        return False

    def playSparkle(self, full=True):
        """Cream flecks timed with cheer pitch swell + delayed cream aftershock."""
        if not getattr(ReclaimGlobals, 'CHEER_CREAM_SPARKLE_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'CHEER_CREAM_SPARKLE_ORIGIN', (0.0, 0.0, 0.06))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.06

        binSort = int(getattr(ReclaimGlobals, 'CHEER_CREAM_SPARKLE_BIN', 53))
        if full:
            count = int(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_COUNT', 12))
            rise = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_RISE', 0.42))
            spread = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_SPREAD', 0.88))
            sec = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_SEC', 0.34))
        else:
            count = int(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_COUNT_WAVE', 7))
            rise = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_RISE_WAVE', 0.28))
            spread = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_SPREAD_WAVE', 0.62))
            sec = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_SPARKLE_SEC_WAVE', 0.26))

        fleckParts = self._spawnFlecks(
            parent, ox, oy, oz, binSort, count, rise, spread, sec)
        if not fleckParts:
            return

        sparkleIval = Parallel(*fleckParts)
        self._sparkleIval = sparkleIval
        try:
            sparkleIval.start()
        except Exception:
            self.clear()
            return

        aftershock = self._buildAftershock(parent, ox, oy, oz, full=full)
        if aftershock is not None:
            # Sparkle Parallel already started; hold its lifetime beside aftershock.
            self._ival = Sequence(
                Parallel(
                    Wait(sec + 0.04),
                    aftershock,
                ),
                Func(self.clear),
                name='reclaimCheerCreamSparkle',
            )
        else:
            self._ival = Sequence(
                Wait(sec + 0.04),
                Func(self.clear),
                name='reclaimCheerCreamSparkle',
            )
        self._ival.start()

    def _spawnFlecks(self, parent, ox, oy, oz, binSort, count, rise, spread, sec):
        """Sunny cream chips — StreetSparkle / EntryCream fleck grammar."""
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_SPARKLE_SIZE', 0.020))
        r, g, b, a = getattr(
            ReclaimGlobals, 'CHEER_CREAM_SPARKLE_COLOR',
            (1.0, 0.98, 0.72, 0.92))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'CHEER_CREAM_SPARKLE_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.22
                cm = CardMaker('reclaim-cheer-cream-sparkle-%s' % i)
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
                startX = ox + t * spread + cos(angle) * 0.03
                startZ = oz + 0.016 * (i % 3) + sin(angle) * 0.016
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.4 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._fleckNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.09,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            delay = 0.016 * i
            twinkle = 0.04 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.12, blendType='easeOut'),
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

    def _buildAftershock(self, parent, ox, oy, oz, full=True):
        """Delayed soft cream flecks (+ optional halo) after cheer sparkle."""
        if not getattr(ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_DELAY_SEC', 0.22))
        parts = []

        if getattr(ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        if full:
            count = int(getattr(
                ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_COUNT', 6))
            sec = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_SEC', 0.38))
        else:
            count = int(getattr(
                ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_COUNT_WAVE', 4))
            sec = float(getattr(
                ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_SEC_WAVE', 0.30))

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
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_HALF', 0.38))
        startScale = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_START', 0.22))
        peakScale = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_PEAK', 1.15))
        sec = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_SEC', 0.30))
        peakA = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.18))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_BIN', 54))
        try:
            cm = CardMaker('reclaim-cheer-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
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
        """Softer cream chip that settles downward — residual cheer aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_SIZE', 0.016))
        drift = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_DRIFT', 0.36))
        fall = float(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_FALL', 0.28))
        r, g, b, a = getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.82))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'CHEER_CREAM_AFTERSHOCK_BIN', 54))
        angle = (2.0 * pi * index) / float(count) + 0.35
        try:
            cm = CardMaker('reclaim-cheer-cream-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the sparkle glitter.
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
            startX = ox + cos(angle) * 0.05
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream, not the sparkle's outward rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.06 * (index % 3))
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
        """Stop sparkle/aftershock and remove every cream cheer node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._sparkleIval is not None:
            try:
                self._sparkleIval.pause()
            except Exception:
                pass
            self._sparkleIval = None
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


def ensureCheerCreamSparkleFxClient():
    global _client
    if _client is None:
        _client = CheerCreamSparkleFxClient()
    return _client

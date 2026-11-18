"""Rubber-hose cream juice for reclaim wave banners.

Wave clear: soft aspect2d cream flash, expanding ring, and sunny flecks.
Wave announce: cream edge-strip pulse framing the wave plate + tip flecks
plus StreetSparkle-style cream sparkle flecks along the cream frame.
Wave-clear cream shimmer hang (WaveClearCreamShimmerFx) follows this burst
as a delayed residual layer, then a quieter cream aftershock, then a soft
cream wash pulse — do not restage flash/ring there.

Layers with ReclaimCheer pitch swell and StreetColorWash — never stomps hood
geom tint / fog / full purity FOV punch. Toontown spiritual-sequel tone only —
no keyblades / no KH branding.
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


class WaveCreamBurstFxClient(DirectObject):
    """Wave-clear cream burst + wave-announce cream edge pulse."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._flashNP = None
        self._ringNP = None
        self._fleckNPs = []
        self._edgeIval = None
        self._edgeRootNP = None
        self._edgeFleckNPs = []
        self._edgeSparkleNPs = []
        self.accept('reclaimWaveCleared', self._onWaveCleared)
        self.accept('reclaimWaveAnnounce', self._onWaveAnnounce)

    def destroy(self):
        self.ignoreAll()
        self.clear()
        self.clearEdge()

    def _onWaveCleared(self, zoneId=None, waveIndex=0):
        self.playBurst()

    def _onWaveAnnounce(self, zoneId=None, waveIndex=0):
        self.playEdgePulse()

    def playBurst(self):
        """Soft cream flash + ring + flecks (no FOV / camera — purity owns that)."""
        if not getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_ORIGIN', (0.0, 0.0, 0.12))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.12

        r, g, b, _a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_COLOR', (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_BIN', 52))
        parts = []

        flashPart = self._spawnFlash(parent, ox, oy, oz, r, g, b, binSort)
        if flashPart is not None:
            parts.append(flashPart)

        ringPart = self._spawnRing(parent, ox, oy, oz, r, g, b, binSort)
        if ringPart is not None:
            parts.append(ringPart)

        fleckParts = self._spawnFlecks(parent, ox, oy, oz, binSort)
        parts.extend(fleckParts)

        if not parts:
            return
        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='reclaimWaveCreamBurst',
        )
        self._ival.start()

    def playEdgePulse(self):
        """Cream border strips + tip flecks + StreetSparkle cream sparkles."""
        if not getattr(ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_ENABLED', True):
            return
        self.clearEdge()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        edgeRoot = self._buildEdgeRoot(parent)
        if edgeRoot is None:
            return

        r, g, b, _a = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        peak = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_PEAK', 0.42))
        mid = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_PULSE', 0.28))
        inSec = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_IN_SEC', 0.08))
        holdSec = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_HOLD_SEC', 0.10))
        pulseSec = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_PULSE_SEC', 0.12))
        outSec = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_OUT_SEC', 0.36))

        # Rubber-hose two-beat: bright pop → soft settle pulse → fade.
        edgePart = Sequence(
            LerpColorScaleInterval(
                edgeRoot, max(0.01, inSec), Vec4(1, 1, 1, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                edgeRoot, max(0.01, pulseSec), Vec4(1, 1, 1, mid),
                blendType='easeInOut'),
            LerpColorScaleInterval(
                edgeRoot, max(0.01, outSec), Vec4(1, 1, 1, 0),
                blendType='easeIn'),
        )
        fleckParts = self._spawnEdgeFlecks(parent)
        sparkleParts = self._spawnEdgeSparkles(parent)
        parts = [edgePart]
        parts.extend(fleckParts)
        parts.extend(sparkleParts)
        self._edgeIval = Sequence(
            Parallel(*parts),
            Func(self.clearEdge),
            name='reclaimWaveCreamEdgePulse',
        )
        self._edgeIval.start()

    def _buildEdgeRoot(self, parent):
        """Four cream edge strips — sunny frame, open center for the banner."""
        try:
            edge = float(getattr(
                ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE', 0.28))
            binSort = int(getattr(
                ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_BIN', 50))
            r, g, b, _a = getattr(
                ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_COLOR',
                (1.0, 0.97, 0.82, 1.0))
            root = parent.attachNewNode('reclaim-wave-cream-edge')
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', binSort)
            root.setDepthTest(False)
            root.setDepthWrite(False)
            # Top / bottom / left / right — cream borders, clear middle.
            frames = (
                (-2.0, 2.0, 1.0 - edge, 1.25),
                (-2.0, 2.0, -1.25, -1.0 + edge),
                (-2.0, -1.0 + edge, -1.25, 1.25),
                (1.0 - edge, 2.0, -1.25, 1.25),
            )
            for i, frame in enumerate(frames):
                cm = CardMaker('reclaim-wave-cream-edge-%s' % i)
                cm.setFrame(*frame)
                strip = root.attachNewNode(cm.generate())
                strip.setTransparency(TransparencyAttrib.MAlpha)
                strip.setColor(r, g, b, 1)
                strip.setBin('fixed', binSort)
                strip.setDepthTest(False)
                strip.setDepthWrite(False)
            self._edgeRootNP = root
            return root
        except Exception:
            self._edgeRootNP = None
            return None

    def _spawnEdgeFlecks(self, parent):
        """Sunny cream chips near the wave plate during the edge pulse."""
        count = int(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_COUNT', 6))
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_SIZE', 0.022))
        drift = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_DRIFT', 0.18))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_SEC', 0.28))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_BIN', 50)) + 1
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_COLOR',
            (1.0, 0.96, 0.62, 0.9))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_END_COLOR',
            (1.0, 0.92, 0.45, 0.0))
        origin = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_FLECK_ORIGIN',
            (0.0, 0.0, 0.72))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.72

        parts = []
        for i in range(count):
            try:
                # Spread along the top banner band (not a full radial burst).
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (0.35 * pi) + (t * 0.9 * pi)
                cm = CardMaker('reclaim-wave-cream-edge-fleck-%s' % i)
                if (i % 2) == 0:
                    cm.setFrame(-size * 1.15, size * 1.15, -size * 0.5, size * 0.5)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                start = Point3(
                    ox + t * 0.55,
                    oy,
                    oz + 0.02 * (i % 3))
                fleck.setPos(start)
                fleck.setScale(0.4 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort)
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._edgeFleckNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                ox + cos(angle) * drift * 0.55 + t * 0.75,
                oy,
                oz + abs(sin(angle)) * drift + 0.04)
            delay = 0.02 * i
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                    LerpScaleInterval(fleck, 0.05, 1.0, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.1, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def _spawnEdgeSparkles(self, parent):
        """StreetSparkle chip/cross flecks rising along the cream edge frame."""
        if not getattr(
                ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_ENABLED',
                True):
            return []
        count = int(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_COUNT', 8))
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SIZE', 0.018))
        rise = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_RISE', 0.30))
        spread = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SPREAD', 1.10))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SEC', 0.36))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_BIN', 50)) + 2
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_COLOR',
            (1.0, 0.98, 0.72, 0.90))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))
        origin = getattr(
            ReclaimGlobals, 'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_ORIGIN',
            (0.0, 0.0, 0.68))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.68

        parts = []
        for i in range(count):
            try:
                # Fan across the top cream strip; chip/cross like StreetSparkle.
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.28
                cm = CardMaker('reclaim-wave-cream-edge-sparkle-%s' % i)
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.30, size * 1.30)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.30, size * 1.30, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                sparkle = parent.attachNewNode(cm.generate())
                sparkle.setTransparency(TransparencyAttrib.MAlpha)
                sparkle.setColor(r, g, b, 1)
                sparkle.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.03
                startZ = oz + 0.016 * (i % 3) + sin(angle) * 0.016
                sparkle.setPos(startX, oy, startZ)
                sparkle.setScale(0.4 + 0.08 * (i % 3))
                sparkle.setBin('fixed', binSort + (i % 2))
                sparkle.setDepthTest(False)
                sparkle.setDepthWrite(False)
                self._edgeSparkleNPs.append(sparkle)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.08,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            delay = 0.018 * i
            twinkle = 0.04 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        sparkle, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        sparkle, twinkle, 1.12, blendType='easeOut'),
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

    def _spawnFlash(self, parent, ox, oy, oz, r, g, b, binSort):
        peak = float(getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLASH_PEAK', 0.34))
        inSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLASH_IN_SEC', 0.05))
        holdSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLASH_HOLD_SEC', 0.06))
        outSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLASH_OUT_SEC', 0.28))
        try:
            cm = CardMaker('reclaim-wave-cream-flash')
            cm.setFrame(-2.0, 2.0, -2.0, 2.0)
            flash = parent.attachNewNode(cm.generate())
            flash.setTransparency(TransparencyAttrib.MAlpha)
            flash.setColor(r, g, b, 1)
            flash.setColorScale(r, g, b, 0)
            flash.setPos(ox, oy, oz)
            flash.setBin('fixed', binSort)
            flash.setDepthTest(False)
            flash.setDepthWrite(False)
            self._flashNP = flash
        except Exception:
            self._flashNP = None
            return None
        return Sequence(
            LerpColorScaleInterval(
                flash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                flash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
        )

    def _spawnRing(self, parent, ox, oy, oz, r, g, b, binSort):
        peakScale = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_RING_PEAK', 1.85))
        sec = float(getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_RING_SEC', 0.36))
        peakA = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_RING_PEAK_ALPHA', 0.48))
        try:
            cm = CardMaker('reclaim-wave-cream-ring')
            cm.setFrame(-0.55, 0.55, -0.55, 0.55)
            ring = parent.attachNewNode(cm.generate())
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, peakA)
            ring.setScale(0.35)
            ring.setPos(ox, oy, oz)
            ring.setBin('fixed', binSort + 1)
            ring.setDepthTest(False)
            ring.setDepthWrite(False)
            self._ringNP = ring
        except Exception:
            self._ringNP = None
            return None
        return Parallel(
            LerpScaleInterval(
                ring, max(0.01, sec), peakScale, blendType='easeOut'),
            LerpColorScaleInterval(
                ring, max(0.01, sec), Vec4(r, g, b, 0), blendType='easeIn'),
        )

    def _spawnFlecks(self, parent, ox, oy, oz, binSort):
        count = int(getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLECK_COUNT', 8))
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLECK_SIZE', 0.028))
        drift = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLECK_DRIFT', 0.42))
        sec = float(getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLECK_SEC', 0.32))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLECK_COLOR',
            (1.0, 0.96, 0.62, 0.95))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_FLECK_END_COLOR',
            (1.0, 0.92, 0.45, 0.0))

        parts = []
        for i in range(count):
            try:
                angle = (2.0 * pi * i) / float(count) + 0.22
                cm = CardMaker('reclaim-wave-cream-fleck-%s' % i)
                # Alternate chip vs fleck — rubber-hose cream bits.
                if (i % 2) == 0:
                    cm.setFrame(-size * 1.2, size * 1.2, -size * 0.55, size * 0.55)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                start = Point3(
                    ox + cos(angle) * 0.05,
                    oy,
                    oz + sin(angle) * 0.04)
                fleck.setPos(start)
                fleck.setScale(0.45 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort + 2)
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._fleckNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                ox + cos(angle) * drift,
                oy,
                oz + sin(angle) * drift * 0.85 + 0.06)
            delay = 0.018 * i
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, 0.06, Vec4(r, g, b, a), blendType='easeOut'),
                    LerpScaleInterval(fleck, 0.06, 1.05, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.08, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
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
        for attr in ('_flashNP', '_ringNP'):
            np = getattr(self, attr, None)
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
            setattr(self, attr, None)
        for np in self._fleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []

    def clearEdge(self):
        if self._edgeIval is not None:
            try:
                self._edgeIval.pause()
            except Exception:
                pass
            self._edgeIval = None
        root = self._edgeRootNP
        self._edgeRootNP = None
        if root is not None and not root.isEmpty():
            try:
                root.removeNode()
            except Exception:
                pass
        for np in self._edgeFleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._edgeFleckNPs = []
        for np in self._edgeSparkleNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._edgeSparkleNPs = []


_client = None


def ensureWaveCreamBurstFxClient():
    global _client
    if _client is None:
        _client = WaveCreamBurstFxClient()
    return _client

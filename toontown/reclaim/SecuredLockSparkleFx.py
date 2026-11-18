"""Secured-street purity lock sparkle + soft audio/HUD sting.

Deepened green-cream aspect2d flecks that celebrate when a reclaim street
hits full purity lock (#205 / #209 deepen) so the street-secure payoff
reads juicier. Distinct from mid-wave warm rim-flash cream (#234),
wave-start sunny hose cream (#239), wave-clear mid-screen cream sparkle
(#229), cheer flecks, and StreetSparkle horizon glitter — this is the
lock-earned tip-near glitter by the purity meter / secured tip.

A quieter sparkle aftershock (settle flecks + soft green-cream halo) hangs
after the rising glitter. Also plays a quiet cheer-cousin pitch sting (not
the full purity whistle, which already fires on purityRestoreFx). Toontown
spiritual-sequel tone only — no KH branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunc,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class SecuredLockSparkleFxClient(DirectObject):
    """Listens for reclaimStreetSecured; owns lock flecks + soft pitch sting."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._sparkleIval = None
        self._pitchIval = None
        self._fleckNPs = []
        self._haloNP = None
        self._sfx = None
        self._lastPlayT = -1.0
        self.accept('reclaimStreetSecured', self._onStreetSecured)
        self.accept('purityRestoreSettled', self._onSettled)

    def destroy(self):
        self.ignoreAll()
        self.clear()

    def _onStreetSecured(self, zoneId=None):
        if self._debounce():
            return
        self.playLockSting()

    def _onSettled(self, zoneId=None):
        self.clear()

    def _debounce(self, minGap=0.45):
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            return False
        if now - self._lastPlayT < float(minGap):
            return True
        self._lastPlayT = now
        return False

    def playLockSting(self):
        """Deepened green-cream flecks near the meter + quiet lock audio sting."""
        if not getattr(ReclaimGlobals, 'SECURED_LOCK_SPARKLE_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_ORIGIN',
            (0.0, 0.0, 0.42))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.42

        count = int(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_COUNT', 10))
        rise = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_RISE', 0.34))
        spread = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_SPREAD', 0.62))
        sec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_SEC', 0.36))
        binSort = int(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_BIN', 54))
        delay = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_DELAY_SEC', 0.03))

        fleckParts = self._spawnFlecks(
            parent, ox, oy, oz, binSort, count, rise, spread, sec)
        if not fleckParts:
            self._playStingSfx()
            return

        sparkleBody = Parallel(*fleckParts)
        aftershock = self._buildSparkleAftershock(parent, ox, oy, oz)
        if aftershock is not None:
            body = Parallel(
                sparkleBody,
                aftershock,
                name='reclaimSecuredLockSparkleBody',
            )
        else:
            body = sparkleBody

        sparkleIval = Sequence(
            Wait(max(0.0, delay)),
            body,
        )
        self._sparkleIval = sparkleIval
        try:
            sparkleIval.start()
        except Exception:
            self.clear()
            return

        self._playStingSfx()

        holdSec = sec + 0.06
        if getattr(
                ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_ENABLED',
                True):
            afterHold = (
                float(getattr(
                    ReclaimGlobals,
                    'SECURED_LOCK_SPARKLE_AFTERSHOCK_DELAY_SEC', 0.16))
                + float(getattr(
                    ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_SEC',
                    0.30))
                + 0.06)
            holdSec = max(holdSec, afterHold)

        self._ival = Sequence(
            Wait(max(0.0, delay) + holdSec),
            Func(self.clear),
            name='reclaimSecuredLockSparkle',
        )
        self._ival.start()

    def _spawnFlecks(self, parent, ox, oy, oz, binSort, count, rise, spread,
                     sec):
        """Green-cream lock chips — Cheer/StreetSparkle fleck grammar, greener."""
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_SIZE', 0.020))
        pop = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_POP', 1.24))
        r, g, b, a = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_COLOR',
            (0.76, 1.0, 0.84, 0.96))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_END_COLOR',
            (0.52, 1.0, 0.70, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.18
                cm = CardMaker('reclaim-secured-lock-sparkle-%s' % i)
                # Alternate chip / cross fleck — rubber-hose lock glitter.
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
                startX = ox + t * spread + cos(angle) * 0.026
                startZ = oz + 0.012 * (i % 3) + sin(angle) * 0.012
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.36 + 0.08 * (i % 3))
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
            stagger = 0.012 * i
            twinkle = 0.040 + 0.01 * (i % 3)
            # Juicier snap: brighter twinkle pop, then ease into the rise fade.
            peakScale = pop + 0.04 * (i % 2)
            parts.append(Sequence(
                Wait(stagger),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, peakScale, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def _buildSparkleAftershock(self, parent, ox, oy, oz):
        """Quieter settle flecks (+ optional halo) after deepened rising sparkle."""
        if not getattr(
                ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_ENABLED',
                True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_DELAY_SEC',
            0.16))
        parts = []

        if getattr(
                ReclaimGlobals,
                'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnSparkleAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_COUNT', 4))
        sec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_SEC', 0.30))
        for i in range(count):
            part = self._spawnSparkleAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
            name='reclaimSecuredLockSparkleAftershock',
        )

    def _spawnSparkleAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_HALF',
            0.34))
        startScale = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_START',
            0.22))
        peakScale = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_PEAK',
            1.16))
        sec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_SEC',
            0.26))
        peakA = float(getattr(
            ReclaimGlobals,
            'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_PEAK_ALPHA', 0.14))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_COLOR',
            (0.78, 1.0, 0.86, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_BIN', 55))
        try:
            cm = CardMaker('reclaim-secured-lock-sparkle-aftershock-halo')
            # Soft oval under tip-near sparkle — greener than wave-clear halo.
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
            name='reclaimSecuredLockSparkleAftershockHalo',
        )

    def _spawnSparkleAftershockFleck(self, parent, ox, oy, oz, index, total,
                                     sec):
        """Softer green-cream chip that settles — residual lock sparkle aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_SIZE', 0.015))
        drift = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_DRIFT', 0.26))
        fall = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_FALL', 0.20))
        r, g, b, a = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_COLOR',
            (0.72, 1.0, 0.82, 0.82))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_END_COLOR',
            (0.50, 0.98, 0.68, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_AFTERSHOCK_BIN', 55))
        angle = (2.0 * pi * index) / float(count) + 0.41
        try:
            cm = CardMaker(
                'reclaim-secured-lock-sparkle-aftershock-%s' % index)
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
            startX = ox + cos(angle) * 0.07
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.26 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.05 * (index % 3))
        peak = 1.04 + 0.06 * (index % 2)
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

    def _ensureSfx(self):
        if self._sfx is not None:
            return self._sfx
        try:
            path = getattr(
                ReclaimGlobals, 'SECURED_LOCK_STING_SFX',
                getattr(
                    ReclaimGlobals, 'PURITY_CHEER_SFX',
                    'phase_3.5/audio/sfx/AV_jump_2.ogg'))
            self._sfx = base.loader.loadSfx(path)  # noqa: F821
        except Exception:
            self._sfx = None
        return self._sfx

    def _playStingSfx(self):
        """Quiet cheer-cousin pitch bump — lock-earned, not full purity whistle."""
        if not getattr(ReclaimGlobals, 'SECURED_LOCK_STING_ENABLED', True):
            return
        sfx = self._ensureSfx()
        if sfx is None:
            return
        if self._pitchIval is not None:
            try:
                self._pitchIval.finish()
            except Exception:
                pass
            self._pitchIval = None

        volume = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_VOLUME', 0.58))
        start = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_PITCH_START', 0.90))
        peak = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_PITCH_PEAK', 1.34))
        end = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_PITCH_END', 1.10))
        swellSec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_SWELL_SEC', 0.11))
        settleSec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_SETTLE_SEC', 0.11))

        def setRate(r):
            try:
                sfx.setPlayRate(float(r))
            except Exception:
                pass

        def startSfx():
            try:
                sfx.setPlayRate(start)
            except Exception:
                pass
            try:
                sfx.setVolume(float(volume))
            except Exception:
                pass
            try:
                base.playSfx(sfx)  # noqa: F821
            except Exception:
                pass

        self._pitchIval = Sequence(
            Func(startSfx),
            LerpFunc(
                setRate,
                fromData=start,
                toData=peak,
                duration=max(0.01, swellSec)),
            LerpFunc(
                setRate,
                fromData=peak,
                toData=end,
                duration=max(0.01, settleSec)),
            name='reclaimSecuredLockSting',
        )
        try:
            self._pitchIval.start()
        except Exception:
            self._pitchIval = None

    def clear(self):
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
        if self._pitchIval is not None:
            try:
                self._pitchIval.finish()
            except Exception:
                pass
            self._pitchIval = None
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


def ensureSecuredLockSparkleFxClient():
    global _client
    if _client is None:
        _client = SecuredLockSparkleFxClient()
    return _client

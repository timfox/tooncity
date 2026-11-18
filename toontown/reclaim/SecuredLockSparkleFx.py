"""Secured-street purity lock sparkle + soft audio/HUD sting.

Short green-cream aspect2d flecks that celebrate when a reclaim street hits
full purity lock (#205). Distinct from mid-wave pressure tip (#202), generic
wave-clear cream sparkle, cheer flecks, and StreetSparkle horizon glitter —
this is the lock-earned glitter near the purity meter / secured tip.

Also plays a quiet cheer-cousin pitch sting (not the full purity whistle,
which already fires on purityRestoreFx). Toontown spiritual-sequel tone only.
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
        """Green-cream flecks near the meter + quiet lock audio sting."""
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
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_COUNT', 7))
        rise = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_RISE', 0.22))
        spread = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_SPREAD', 0.48))
        sec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_SEC', 0.30))
        binSort = int(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_BIN', 54))
        delay = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_DELAY_SEC', 0.04))

        fleckParts = self._spawnFlecks(
            parent, ox, oy, oz, binSort, count, rise, spread, sec)
        if not fleckParts:
            self._playStingSfx()
            return

        sparkleIval = Sequence(
            Wait(max(0.0, delay)),
            Parallel(*fleckParts),
        )
        self._sparkleIval = sparkleIval
        try:
            sparkleIval.start()
        except Exception:
            self.clear()
            return

        self._playStingSfx()

        self._ival = Sequence(
            Wait(max(0.0, delay) + sec + 0.06),
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
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_SIZE', 0.017))
        r, g, b, a = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_COLOR',
            (0.78, 1.0, 0.86, 0.92))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'SECURED_LOCK_SPARKLE_END_COLOR',
            (0.55, 1.0, 0.72, 0.0))

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
                startX + cos(angle) * 0.07,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            stagger = 0.014 * i
            twinkle = 0.035 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(stagger),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.14, blendType='easeOut'),
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
            ReclaimGlobals, 'SECURED_LOCK_STING_VOLUME', 0.55))
        start = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_PITCH_START', 0.92))
        peak = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_PITCH_PEAK', 1.28))
        end = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_PITCH_END', 1.08))
        swellSec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_SWELL_SEC', 0.10))
        settleSec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_STING_SETTLE_SEC', 0.10))

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

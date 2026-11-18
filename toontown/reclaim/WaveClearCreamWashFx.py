"""Rubber-hose cream wash pulse after reclaim wave-clear cream aftershock.

Fullscreen soft cream veil that settles *after* WaveClearCreamShimmerFx cream
aftershock (#127) / clear shimmer (#93) — CheerCreamWashPulse /
PurityCompleteCreamWashFx / EntryCreamWashPulseFx overlay grammar as a brief
wave-clear settle beat. Soft under shimmer flecks; cream / pastel only (not
ink). A delayed cream sparkle residual (rising chip/cross flecks —
CheerCreamSparkle / StreetSparkle / wave-edge sparkle grammar) follows the
wash pulse so the settle beat keeps a quiet glitter lift without restaging
the shimmer hang or cheer swell flecks. Wired from
WaveClearCreamShimmerFx.playHang beside the cream aftershock. Client only.
Toontown spiritual sequel — no keyblades / no KH branding.
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

from toontown.reclaim import ReclaimGlobals


class WaveClearCreamWashPulse(object):
    """Owns aspect2d cream wash pulse + residual cream sparkle after wash."""

    def __init__(self):
        self._ival = None
        self._washNP = None
        self._sparkleNPs = []

    def play(self, delay=None):
        """Arm delayed two-beat cream wash + sparkle. Returns Sequence or None."""
        if not getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_PEAK', 0.10))
        mid = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_MID', 0.05))
        inSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_IN_SEC', 0.05))
        pulseSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_PULSE_SEC', 0.09))
        holdSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_HOLD_SEC', 0.06))
        outSec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_OUT_SEC', 0.34))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_BIN', 50))
        if delay is None:
            delay = float(getattr(
                ReclaimGlobals, 'WAVE_CLEAR_CREAM_WASH_DELAY_SEC', 0.40))

        try:
            cm = CardMaker('reclaim-wave-clear-cream-wash')
            # Full-frame veil — cheer / entry / purity cream wash grammar.
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
        washVeil = Sequence(
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
            name='reclaimWaveClearCreamWashVeil',
        )

        sparkle = self._buildSparkle(parent)

        # Arm wash + residual sparkle after the shared delay from hang start.
        if sparkle is not None:
            body = Parallel(
                washVeil,
                sparkle,
            )
        else:
            body = washVeil

        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            body,
            Wait(0.04),
            Func(self.clear),
            name='reclaimWaveClearCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildSparkle(self, parent):
        """Delayed rising cream sparkle flecks after wave-clear wash starts."""
        if not getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_ENABLED', True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_DELAY_SEC', 0.12))
        origin = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_ORIGIN',
            (0.0, 0.0, 0.08))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.08

        count = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_COUNT', 6))
        rise = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_RISE', 0.24))
        spread = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_SPREAD', 0.58))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_SEC', 0.28))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_BIN', 53))
        fleckParts = self._spawnSparkleFlecks(
            parent, ox, oy, oz, binSort, count, rise, spread, sec)
        if not fleckParts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*fleckParts),
        )

    def _spawnSparkleFlecks(self, parent, ox, oy, oz, binSort, count, rise,
                            spread, sec):
        """Sunny cream chips — CheerCreamSparkle / StreetSparkle fleck grammar."""
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_SIZE', 0.018))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_COLOR',
            (1.0, 0.98, 0.72, 0.88))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.26
                cm = CardMaker('reclaim-wave-clear-cream-sparkle-%s' % i)
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
                startX = ox + t * spread + cos(angle) * 0.028
                startZ = oz + 0.014 * (i % 3) + sin(angle) * 0.014
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.38 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._sparkleNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.08,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            stagger = 0.016 * i
            twinkle = 0.04 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(stagger),
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

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._washNP
        self._washNP = None
        if wash is not None:
            try:
                if not wash.isEmpty():
                    wash.removeNode()
            except Exception:
                pass
        for np in self._sparkleNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._sparkleNPs = []

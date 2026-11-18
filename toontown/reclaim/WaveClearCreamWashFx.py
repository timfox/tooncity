"""Rubber-hose cream wash pulse after reclaim wave-clear cream aftershock.

Fullscreen soft cream veil that settles *after* WaveClearCreamShimmerFx cream
aftershock (#127) / clear shimmer (#93) — CheerCreamWashPulse /
PurityCompleteCreamWashFx / EntryCreamWashPulseFx overlay grammar as a brief
wave-clear settle beat. Soft under shimmer flecks; cream / pastel only (not
ink). A further-deepened cream sparkle residual past #273 (rising chip/cross
flecks + juicier twinkle pop — CheerCreamSparkle / StreetSparkle / wave-edge
sparkle grammar) follows the wash pulse so pack clear feels juicier without
restaging the shimmer hang, cheer swell flecks, secured-lock tip-near green
sting (#286), purity-complete meter hose settle cream (#292), mid-wave warm
rim flash, or wave-start meter hose pop. A quieter sparkle aftershock
(settle flecks + soft halo) hangs after the rising glitter. Wired from
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
    """Owns aspect2d cream wash pulse + further-deepened residual cream sparkle."""

    def __init__(self):
        self._ival = None
        self._washNP = None
        self._sparkleNPs = []
        self._haloNP = None

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
        """Further-deepened rising cream sparkle + optional soft aftershock."""
        if not getattr(ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_ENABLED', True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_DELAY_SEC', 0.06))
        origin = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_ORIGIN',
            (0.0, 0.0, 0.08))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.08

        count = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_COUNT', 13))
        rise = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_RISE', 0.50))
        spread = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_SPREAD', 1.00))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_SEC', 0.48))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_BIN', 53))
        fleckParts = self._spawnSparkleFlecks(
            parent, ox, oy, oz, binSort, count, rise, spread, sec)
        if not fleckParts:
            return None

        sparkleBody = Parallel(*fleckParts)
        aftershock = self._buildSparkleAftershock(parent, ox, oy, oz)
        if aftershock is not None:
            body = Parallel(
                sparkleBody,
                aftershock,
            )
        else:
            body = sparkleBody
        return Sequence(
            Wait(max(0.0, delay)),
            body,
        )

    def _spawnSparkleFlecks(self, parent, ox, oy, oz, binSort, count, rise,
                            spread, sec):
        """Sunny cream chips — CheerCreamSparkle / StreetSparkle fleck grammar."""
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_SIZE', 0.027))
        pop = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_POP', 1.46))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_COLOR',
            (1.0, 0.98, 0.66, 0.98))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_END_COLOR',
            (1.0, 0.94, 0.48, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.18
                cm = CardMaker('reclaim-wave-clear-cream-sparkle-%s' % i)
                # Alternate chip / cross fleck — rubber-hose cream glitter.
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.40, size * 1.40)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.40, size * 1.40, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.036
                startZ = oz + 0.018 * (i % 3) + sin(angle) * 0.018
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.46 + 0.11 * (i % 3))
                fleck.setBin('fixed', binSort + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._sparkleNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.14,
                oy,
                startZ + rise * (0.56 + 0.44 * ((i % 4) / 3.0)))
            stagger = 0.010 * i
            twinkle = 0.054 + 0.012 * (i % 3)
            # Juicier pack snap past #273: brighter twinkle pop, then rise fade.
            peakScale = pop + 0.07 * (i % 2)
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
        """Quieter settle flecks (+ optional halo) after further-deepened sparkle."""
        if not getattr(
                ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_ENABLED',
                True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_DELAY_SEC',
            0.12))
        parts = []

        if getattr(
                ReclaimGlobals,
                'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnSparkleAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_COUNT', 7))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_SEC', 0.42))
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
        )

    def _spawnSparkleAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_HALF',
            0.48))
        startScale = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_START',
            0.32))
        peakScale = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_PEAK',
            1.30))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_SEC',
            0.36))
        peakA = float(getattr(
            ReclaimGlobals,
            'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_PEAK_ALPHA', 0.19))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.76, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_BIN', 54))
        try:
            cm = CardMaker('reclaim-wave-clear-cream-sparkle-aftershock-halo')
            # Soft oval under mid-screen sparkle — quieter than shimmer halo.
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

    def _spawnSparkleAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual sparkle aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_SIZE', 0.021))
        drift = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_DRIFT', 0.40))
        fall = float(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_FALL', 0.32))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.72, 0.90))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.50, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_BIN', 54))
        angle = (2.0 * pi * index) / float(count) + 0.34
        try:
            cm = CardMaker(
                'reclaim-wave-clear-cream-sparkle-aftershock-%s' % index)
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.30, size * 1.30)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.30, size * 1.30, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.10
            startZ = oz + 0.016 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.32 + 0.10 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        end = Point3(
            startX + cos(angle) * drift * 0.62,
            oy,
            startZ - fall - 0.065 * (index % 3))
        peak = 1.12 + 0.09 * (index % 2)
        self._sparkleNPs.append(fleck)
        stagger = 0.012 * (index % 3)
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
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._sparkleNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._sparkleNPs = []

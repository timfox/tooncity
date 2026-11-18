"""Cream splash + delayed cream aftershock on Sludge Brute spit impact / land.

World-space CardMaker juice that fires when the green spit blob lands after
the telegraph spit-gob wind-up — sunny cream / pastel contrast against the
green BRUTE_SPIT_BLOB_* so the tank spit reads juicy (rubber-hose corruption
feel). Deepened spit-land juice beyond #264: juicier splat/flecks, thicker
vertical cream drip filaments (spit-gob fall read), then a heavier downward
settle aftershock (halo + residual flecks) — distinct from Snare counter
cream deepen (#269 / #245, horizontal whip filaments), Gunk puddle cream
deepen (#276 / #238, flat ground bloom), and Smudge hit cream deepen
(#283 / #259, radial hose smears). Same residual grammar as telegraph cream
warn aftershock (#121). Wired from DistributedCorruptToon.__playSpitBlob.
Client only. Toontown spiritual sequel — no keyblades / no KH branding.
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

from toontown.corruption import CorruptionGlobals


def bruteSpitCreamSplashLook():
    """Resolve cream splash palette / motion; compose delay with spit travel."""
    look = dict(getattr(
        CorruptionGlobals, 'BRUTE_SPIT_CREAM_SPLASH_LOOK', {}) or {})
    # Land splash as the green spit blob arrives — not sync-locked with gob.
    travel = float(getattr(CorruptionGlobals, 'BRUTE_SPIT_BLOB_TRAVEL', 0.28))
    look.setdefault(
        'delaySec',
        travel * float(look.get('delayScale', 0.95)))
    # Impact is already lifted toward the local toon; keep a small cream pop.
    look.setdefault(
        'lift',
        float(getattr(
            CorruptionGlobals, 'BRUTE_SPIT_CREAM_SPLASH_LIFT', 0.35)))
    look.setdefault(
        'binSort',
        int(getattr(
            CorruptionGlobals, 'BRUTE_SPIT_CREAM_SPLASH_BIN', 41)))
    return look


class BruteSpitCreamSplash(object):
    """Owns brief cream splash + delayed cream aftershock at spit land pos."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._haloNP = None

    def play(self, pos, parent=None, delay=None):
        """Spawn cream splash + aftershock at `pos`. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_SPLASH_ENABLED', True):
            return None
        self.clear()
        look = bruteSpitCreamSplashLook()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look.get('lift', 0.35)))

        if delay is None:
            delay = float(look.get(
                'delaySec',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DELAY_SEC', 0.26)))

        parts = []
        splat = self._spawnSplat(parentNP, origin, look)
        if splat is not None:
            parts.append(splat)

        dripCount = max(0, int(look.get('dripCount', 0)))
        if look.get(
                'dripEnabled',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DRIP_ENABLED', True)):
            for i in range(dripCount):
                part = self._spawnDripFilament(parentNP, origin, look, i)
                if part is not None:
                    parts.append(part)

        fleckCount = max(0, int(look.get('fleckCount', 0)))
        for i in range(fleckCount):
            part = self._spawnFleck(parentNP, origin, look, i, fleckCount)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        splashParallel = Parallel(*parts)
        aftershock = self._buildAftershock(parentNP, origin)
        body = splashParallel
        if aftershock is not None:
            body = Parallel(splashParallel, aftershock)

        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            body,
            Func(self.clear),
            name='bruteSpitCreamSplash',
        )
        self._ival.start()
        return self._ival

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in list(self._nodes):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _spawnSplat(self, parentNP, origin, look):
        """Tiny billboard cream blob — spit-land readability core."""
        try:
            half = float(look.get('splatHalf', 0.3))
            cm = CardMaker('brute-spit-cream-splash-core')
            cm.setFrame(-half, half, -half * 0.92, half * 0.92)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'splatColor',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_COLOR',
                    (1.0, 0.97, 0.82, 0.96)))
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0)
            splat.setScale(0.34)
            splat.setBin('fixed', int(look.get('binSort', 41)))
            splat.setDepthWrite(False)
            self._nodes.append(splat)

            rimHalf = half * float(look.get('rimScale', 1.48))
            cmRim = CardMaker('brute-spit-cream-splash-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.9)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin)
            rim.setBillboardPointEye()
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get(
                'rimColor',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_RIM_COLOR',
                    (1.0, 0.98, 0.88, 0.86)))
            rim.setColor(rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.3)
            rim.setBin('fixed', int(look.get('binSort', 41)) - 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('splatPeak', 2.05))
            sec = float(look.get('splatSec', 0.21))
            peakA = float(look.get('peakAlpha', 0.99))
            return Parallel(
                Sequence(
                    LerpColorScaleInterval(
                        splat, sec * 0.2, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        splat, sec * 0.8, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(splat, sec, peak, blendType='easeOut'),
                Sequence(
                    LerpColorScaleInterval(
                        rim, sec * 0.16, Vec4(1, 1, 1, 0.74),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        rim, sec * 0.84, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(
                    rim, sec, peak * 1.22, blendType='easeOut'),
            )
        except Exception:
            return None

    def _spawnDripFilament(self, parentNP, origin, look, index):
        """Vertical cream drip filament — spit-gob fall / land cue.

        Distinct from Snare horizontal whip filaments (#269 / #245), Gunk
        flat puddle-plane bloom (#276 / #238), and Smudge radial hose
        (#283 / #259): tall downward cream smear matching green spit-blob
        land grammar (BruteSpitTelegraphFx gob cousin).
        """
        try:
            side = -1.0 if (index % 2) == 0 else 1.0
            t = 0.48 + 0.22 * (index // 2)
            # Bias downward so the cream drip reads as spit gob settling.
            spreadX = side * (0.2 + 0.13 * index) * t
            spreadY = (0.09 * ((index % 3) - 1)) * t
            fall = float(look.get(
                'dripFall',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DRIP_FALL', 1.25)))
            end = Point3(
                origin[0] + spreadX,
                origin[1] + spreadY,
                origin[2] - fall * (0.72 + 0.14 * (index % 3)),
            )
            half = float(look.get(
                'dripHalf',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DRIP_HALF', 0.1)))
            cm = CardMaker(
                'brute-spit-cream-splash-drip-%s' % index)
            # Tall / thin frame — cream drip, not whip filament / puddle bloom.
            cm.setFrame(-half * 0.45, half * 0.45, -half * 1.85, half * 1.85)
            drip = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + side * 0.055,
                origin[1] + 0.03 * ((index % 2) - 0.5),
                origin[2] + 0.16 + 0.055 * (index % 3),
            )
            drip.setPos(start)
            drip.setBillboardPointEye()
            drip.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'dripColor',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DRIP_COLOR',
                    (1.0, 0.97, 0.84, 0.96)))
            tint = 0.92 + 0.06 * (index % 3)
            drip.setColor(
                min(1.4, color[0] * tint),
                min(1.4, color[1] * tint),
                min(1.4, color[2] * tint),
                color[3])
            drip.setColorScale(1, 1, 1, 0)
            drip.setScale(Point3(0.4, 0.4, 0.65))
            drip.setBin('fixed', int(look.get('binSort', 41)) + 1)
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look.get(
                'dripSec',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DRIP_SEC', 0.28)))
            peakA = float(look.get(
                'dripPeakAlpha',
                getattr(
                    CorruptionGlobals,
                    'BRUTE_SPIT_CREAM_SPLASH_DRIP_PEAK_ALPHA',
                    0.96)))
            delay = 0.01 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(drip, travel, end, blendType='easeIn'),
                    Sequence(
                        LerpScaleInterval(
                            drip, travel * 0.3, Point3(0.8, 0.8, 1.85),
                            blendType='easeOut'),
                        LerpScaleInterval(
                            drip, travel * 0.7, Point3(0.16, 0.16, 2.2),
                            blendType='easeIn'),
                    ),
                    Sequence(
                        LerpColorScaleInterval(
                            drip, travel * 0.18, Vec4(1, 1, 1, peakA),
                            blendType='easeOut'),
                        LerpColorScaleInterval(
                            drip, travel * 0.82, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
            )
        except Exception:
            return None

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Outward cream fleck — telegraph cream warn / spit-land cousin."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + (0.16 * (index % 3))
            dist = float(look.get('fleckDist', 1.05)) * (
                0.55 + 0.16 * (index % 4))
            lift = float(look.get('fleckLift', 0.48)) * (
                0.4 + 0.18 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.1))
            if index % 2 == 0:
                cm = CardMaker(
                    'brute-spit-cream-splash-fleck-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.35, 0.35, 0.35)
                midScale = Point3(1.15, 1.15, 0.55)
                endScale = Point3(1.45, 1.45, 0.12)
            else:
                cm = CardMaker(
                    'brute-spit-cream-splash-streak-%s' % index)
                cm.setFrame(
                    -half * 0.32, half * 0.32, -half * 1.45, half * 1.45)
                startScale = Point3(0.28, 0.28, 0.6)
                midScale = Point3(0.5, 0.5, 1.35)
                endScale = Point3(1.2, 0.2, 0.14)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            colors = look.get('fleckColors') or getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_SPLASH_FLECK_COLORS',
                ((1.0, 0.97, 0.82, 0.9),))
            color = colors[index % len(colors)]
            fleck.setColor(color[0], color[1], color[2], color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 41)) + 1)
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.2))
            delay = 0.01 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.45, midScale),
                        LerpScaleInterval(fleck, travel * 0.55, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _buildAftershock(self, parentNP, origin):
        """Delayed soft cream flecks (+ optional halo) after the cream splash."""
        if not getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_DELAY_SEC', 0.14))
        parts = []

        if getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_COUNT', 5)))
        streakCount = max(0, int(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_COUNT', 2)))
        for i in range(creamCount):
            part = self._spawnAftershockSpark(
                parentNP, origin, i, creamCount, elongated=False)
            if part is not None:
                parts.append(part)
        for i in range(streakCount):
            part = self._spawnAftershockSpark(
                parentNP, origin, i, streakCount, elongated=True)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parentNP, origin):
        half = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_HALF', 0.54))
        startScale = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_START', 0.3))
        peakScale = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_PEAK', 1.6))
        sec = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_SEC', 0.32))
        peakA = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.24))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        try:
            cm = CardMaker('brute-spit-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            binSort = int(getattr(
                CorruptionGlobals, 'BRUTE_SPIT_CREAM_SPLASH_BIN', 41))
            halo.setBin('fixed', binSort - 1)
            halo.setDepthWrite(False)
            halo.setBillboardPointEye()
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

    def _spawnAftershockSpark(self, parentNP, origin, index, total,
                              elongated=False):
        """Softer cream fleck / streak that settles — residual aftershock."""
        count = max(1, int(total))
        if elongated:
            size = float(getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_SIZE', 0.12))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.82))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.45
        else:
            size = float(getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_SIZE', 0.1))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.85))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.18
        drift = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_DRIFT', 0.72))
        fall = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_FALL', 0.55))
        sec = float(getattr(
            CorruptionGlobals,
            'BRUTE_SPIT_CREAM_AFTERSHOCK_SEC', 0.36))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'brute-spit-cream-aftershock-%s-%s' % (
                    nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -size * 0.35, size * 0.35,
                    -size * 1.15, size * 1.15)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            spark = parentNP.attachNewNode(cm.generate())
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(r, g, b, 1)
            spark.setColorScale(r, g, b, a)
            spark.setPos(
                origin[0] + cos(angle) * 0.1,
                origin[1] + sin(angle) * 0.1,
                origin[2] + 0.02 * (index % 2))
            spark.setScale(0.26 + 0.06 * (index % 3))
            binSort = int(getattr(
                CorruptionGlobals, 'BRUTE_SPIT_CREAM_SPLASH_BIN', 41))
            spark.setBin('fixed', binSort)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            return None

        # Heavier downward settle after spit land (beyond #264 drip residual).
        end = Point3(
            origin[0] + cos(angle) * drift * 0.45,
            origin[1] + sin(angle) * drift * 0.45,
            origin[2] - fall - 0.12 * (index % 3))
        peak = size * (1.28 + 0.12 * (index % 2))
        self._nodes.append(spark)
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    spark, max(0.01, sec), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
                LerpPosInterval(
                    spark, max(0.01, sec), end, blendType='easeIn'),
                Sequence(
                    LerpScaleInterval(
                        spark, max(0.01, sec * 0.36), peak,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        spark, max(0.01, sec * 0.64), 0.09,
                        blendType='easeIn'),
                ),
            ),
        )

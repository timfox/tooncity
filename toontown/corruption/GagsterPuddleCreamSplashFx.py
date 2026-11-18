"""Cream splash + delayed cream aftershock on Gunk Gagster puddle land / splash.

World-space CardMaker juice that fires when the teal gag-lob puddle lands —
sunny cream / pastel contrast against the teal GAGSTER_PUDDLE_* trap so the
impact reads juicy after the telegraph puddle warn (#197). Deepened ground-
trap juice beyond #276: juicier splat/flecks, a thicker flat cream bloom on
the puddle plane, then a wider settling aftershock (halo + residual flecks)
— distinct from Smudge hit cream deepen (#283 / #259, radial hose), Brute
spit cream deepen (#289 / #264, vertical drip), and Snare counter cream
deepen (#293 / #269, horizontal whip). Same residual grammar as telegraph
cream warn aftershock (#121) / Snare counter cream splash (#214). Wired from
DistributedCorruptToon.__playGagPuddle. Client only. Toontown spiritual
sequel — no keyblades / no KH branding.
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


def gagsterPuddleCreamSplashLook():
    """Resolve cream splash palette / motion; compose delay with teal puddle."""
    look = dict(getattr(
        CorruptionGlobals, 'GAGSTER_PUDDLE_CREAM_SPLASH_LOOK', {}) or {})
    # Land splash as the teal puddle blooms — not sync-locked with peak scale.
    puddleSec = float(getattr(CorruptionGlobals, 'GAGSTER_PUDDLE_SEC', 0.28))
    look.setdefault(
        'delaySec',
        puddleSec * float(look.get('delayScale', 0.12)))
    # Ground trap — low lift above the flat puddle ring.
    look.setdefault(
        'lift',
        float(getattr(
            CorruptionGlobals, 'GAGSTER_PUDDLE_CREAM_SPLASH_LIFT', 0.56)))
    look.setdefault(
        'binSort',
        int(getattr(
            CorruptionGlobals, 'GAGSTER_PUDDLE_CREAM_SPLASH_BIN', 40)))
    return look


class GagsterPuddleCreamSplash(object):
    """Owns brief cream splash + delayed cream aftershock at puddle land pos."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._haloNP = None

    def play(self, pos, parent=None, delay=None):
        """Spawn cream splash + aftershock at `pos`. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_SPLASH_ENABLED', True):
            return None
        self.clear()
        look = gagsterPuddleCreamSplashLook()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look.get('lift', 0.56)))

        if delay is None:
            delay = float(look.get(
                'delaySec',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_DELAY_SEC', 0.06)))

        parts = []
        splat = self._spawnSplat(parentNP, origin, look)
        if splat is not None:
            parts.append(splat)

        bloom = self._spawnGroundBloom(parentNP, origin, look)
        if bloom is not None:
            parts.append(bloom)

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
            name='gagsterPuddleCreamSplash',
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
        """Tiny billboard cream blob — puddle-land readability core."""
        try:
            half = float(look.get('splatHalf', 0.4))
            cm = CardMaker('gagster-puddle-cream-splash-core')
            cm.setFrame(-half, half, -half * 0.92, half * 0.92)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'splatColor',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_COLOR',
                    (1.0, 0.97, 0.82, 0.98)))
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0)
            splat.setScale(0.3)
            splat.setBin('fixed', int(look.get('binSort', 40)))
            splat.setDepthWrite(False)
            self._nodes.append(splat)

            rimHalf = half * float(look.get('rimScale', 1.45))
            cmRim = CardMaker('gagster-puddle-cream-splash-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.9)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin)
            rim.setBillboardPointEye()
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get(
                'rimColor',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_RIM_COLOR',
                    (1.0, 0.98, 0.88, 0.82)))
            rim.setColor(rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.26)
            rim.setBin('fixed', int(look.get('binSort', 40)) - 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('splatPeak', 2.15))
            sec = float(look.get('splatSec', 0.2))
            peakA = float(look.get('peakAlpha', 0.98))
            return Parallel(
                Sequence(
                    LerpColorScaleInterval(
                        splat, sec * 0.22, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        splat, sec * 0.78, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(splat, sec, peak, blendType='easeOut'),
                Sequence(
                    LerpColorScaleInterval(
                        rim, sec * 0.18, Vec4(1, 1, 1, 0.7),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        rim, sec * 0.82, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(
                    rim, sec, peak * 1.18, blendType='easeOut'),
            )
        except Exception:
            return None

    def _spawnGroundBloom(self, parentNP, origin, look):
        """Flat cream bloom on the puddle plane — ground-trap land cue.

        Distinct from Smudge mid-body radial hose (#283 / #259), Brute
        vertical drip (#289 / #264), and Snare horizontal whip (#293 / #269):
        lies on the trap ring (setP -90) and blooms thicker beyond #276 as
        the teal puddle lands.
        """
        if not look.get(
                'bloomEnabled',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_ENABLED', True)):
            return None
        try:
            half = float(look.get(
                'bloomHalf',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_HALF', 1.0)))
            cm = CardMaker('gagster-puddle-cream-splash-bloom')
            cm.setFrame(-half, half, -half, half)
            bloom = parentNP.attachNewNode(cm.generate())
            # Sit just under the billboard splat lift on the puddle plane.
            bloomLift = float(getattr(
                CorruptionGlobals, 'GAGSTER_PUDDLE_CREAM_SPLASH_LIFT', 0.56))
            bloom.setPos(
                origin[0], origin[1],
                origin[2] - bloomLift + 0.05)
            bloom.setP(-90)
            bloom.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'bloomColor',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_COLOR',
                    (1.0, 0.97, 0.84, 0.8)))
            bloom.setColor(color[0], color[1], color[2], color[3])
            bloom.setColorScale(1, 1, 1, 0)
            bloom.setScale(0.3)
            bloom.setBin('fixed', int(look.get('binSort', 40)) - 1)
            bloom.setDepthWrite(False)
            self._nodes.append(bloom)

            peak = float(look.get(
                'bloomPeak',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_PEAK', 2.65)))
            sec = float(look.get(
                'bloomSec',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_SEC', 0.32)))
            peakA = float(look.get(
                'bloomPeakAlpha',
                getattr(
                    CorruptionGlobals,
                    'GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_PEAK_ALPHA', 0.72)))
            return Parallel(
                Sequence(
                    LerpColorScaleInterval(
                        bloom, sec * 0.24, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        bloom, sec * 0.76, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(bloom, sec, peak, blendType='easeOut'),
            )
        except Exception:
            return None

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Outward cream fleck — telegraph cream warn / puddle warn cousin."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + (0.14 * (index % 3))
            dist = float(look.get('fleckDist', 1.65)) * (
                0.55 + 0.18 * (index % 4))
            lift = float(look.get('fleckLift', 0.42)) * (
                0.38 + 0.2 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.13))
            if index % 2 == 0:
                cm = CardMaker(
                    'gagster-puddle-cream-splash-fleck-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.32, 0.32, 0.32)
                midScale = Point3(1.22, 1.22, 0.58)
                endScale = Point3(1.55, 1.55, 0.1)
            else:
                cm = CardMaker(
                    'gagster-puddle-cream-splash-streak-%s' % index)
                cm.setFrame(
                    -half * 0.3, half * 0.3, -half * 1.55, half * 1.55)
                startScale = Point3(0.26, 0.26, 0.62)
                midScale = Point3(0.52, 0.52, 1.45)
                endScale = Point3(1.3, 0.18, 0.12)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            colors = look.get('fleckColors') or getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_SPLASH_FLECK_COLORS',
                ((1.0, 0.97, 0.82, 0.96),))
            color = colors[index % len(colors)]
            fleck.setColor(color[0], color[1], color[2], color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 40)) + 1)
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.28))
            delay = 0.009 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.42, midScale),
                        LerpScaleInterval(fleck, travel * 0.58, endScale),
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
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_DELAY_SEC', 0.12))
        parts = []

        if getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_COUNT', 6)))
        streakCount = max(0, int(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_COUNT', 3)))
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
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_HALF', 0.68))
        startScale = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_START', 0.28))
        peakScale = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_PEAK', 1.9))
        sec = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_SEC', 0.36))
        peakA = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.3))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        try:
            cm = CardMaker('gagster-puddle-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            binSort = int(getattr(
                CorruptionGlobals, 'GAGSTER_PUDDLE_CREAM_SPLASH_BIN', 40))
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
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_SIZE', 0.12))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.82))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.45
        else:
            size = float(getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_SIZE', 0.1))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.85))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.18
        drift = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_DRIFT', 0.65))
        fall = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_FALL', 0.35))
        sec = float(getattr(
            CorruptionGlobals,
            'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_SEC', 0.34))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'gagster-puddle-cream-aftershock-%s-%s' % (
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
                CorruptionGlobals, 'GAGSTER_PUDDLE_CREAM_SPLASH_BIN', 40))
            spark.setBin('fixed', binSort)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            return None

        # Wider sideways settle onto the puddle plane (beyond #276 residual).
        end = Point3(
            origin[0] + cos(angle) * drift * 0.68,
            origin[1] + sin(angle) * drift * 0.68,
            origin[2] - fall - 0.08 * (index % 3))
        peak = size * (1.28 + 0.1 * (index % 2))
        self._nodes.append(spark)
        stagger = 0.018 * (index % 3)
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
                        spark, max(0.01, sec * 0.38), peak,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        spark, max(0.01, sec * 0.62), 0.1,
                        blendType='easeIn'),
                ),
            ),
        )

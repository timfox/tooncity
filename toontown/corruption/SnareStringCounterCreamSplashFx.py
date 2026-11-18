"""Cream splash + delayed cream aftershock on Balloon Snare string-snap counter.

World-space CardMaker juice that fires when a Snare string-snap punish /
counter lands successfully — sunny cream / pastel contrast against the amber
SnareStringSnapSplashFx (#84) so the rewarded window reads juicy. Immediate
cream splat/flecks, then a soft settling aftershock (halo + residual flecks)
matching telegraph cream warn aftershock grammar (#121). Wired from
DistributedCorruptToon hit reaction when the string-snap counter juice window
is live. Client only. Toontown spiritual sequel — no keyblades / no KH branding.
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


def snareStringCounterCreamSplashLook():
    """Resolve cream splash palette / motion; compose lift with amber snap."""
    look = dict(getattr(
        CorruptionGlobals, 'SNARE_STRING_COUNTER_CREAM_SPLASH_LOOK', {}) or {})
    # Lazy import avoids circular load with SnareStringSnapSplashFx.
    try:
        from toontown.corruption.SnareStringSnapSplashFx import (
            snareStringSnapSplashLook)
        amber = snareStringSnapSplashLook('hit')
        look.setdefault('lift', float(amber.get('lift', 1.95)))
        # Land splash as amber snap settles — not sync-locked with smack peak.
        splatSec = float(amber.get('splatSec', 0.16))
        look.setdefault(
            'delaySec',
            splatSec * float(look.get('delayScale', 0.35)))
    except Exception:
        look.setdefault('lift', 1.95)
        look.setdefault(
            'delaySec',
            float(getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_SPLASH_DELAY_SEC', 0.06)))
    look.setdefault(
        'binSort',
        int(getattr(
            CorruptionGlobals, 'SNARE_STRING_COUNTER_CREAM_SPLASH_BIN', 46)))
    return look


class SnareStringCounterCreamSplash(object):
    """Owns brief cream splash + delayed cream aftershock at a world position."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._haloNP = None

    def play(self, pos, parent=None, delay=None):
        """Spawn cream splash + aftershock at `pos`. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_SPLASH_ENABLED', True):
            return None
        self.clear()
        look = snareStringCounterCreamSplashLook()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look.get('lift', 1.95)))

        if delay is None:
            delay = float(look.get(
                'delaySec',
                getattr(
                    CorruptionGlobals,
                    'SNARE_STRING_COUNTER_CREAM_SPLASH_DELAY_SEC', 0.06)))

        parts = []
        splat = self._spawnSplat(parentNP, origin, look)
        if splat is not None:
            parts.append(splat)

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
            name='snareStringCounterCreamSplash',
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
        """Tiny billboard cream blob — rewarded punish readability core."""
        try:
            half = float(look.get('splatHalf', 0.22))
            cm = CardMaker('snare-string-counter-cream-splash-core')
            cm.setFrame(-half, half, -half * 0.92, half * 0.92)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'splatColor',
                getattr(
                    CorruptionGlobals,
                    'SNARE_STRING_COUNTER_CREAM_SPLASH_COLOR',
                    (1.0, 0.97, 0.82, 0.94)))
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0)
            splat.setScale(0.32)
            splat.setBin('fixed', int(look.get('binSort', 46)))
            splat.setDepthWrite(False)
            self._nodes.append(splat)

            rimHalf = half * float(look.get('rimScale', 1.28))
            cmRim = CardMaker('snare-string-counter-cream-splash-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.9)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin)
            rim.setBillboardPointEye()
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get(
                'rimColor',
                getattr(
                    CorruptionGlobals,
                    'SNARE_STRING_COUNTER_CREAM_SPLASH_RIM_COLOR',
                    (1.0, 0.98, 0.88, 0.7)))
            rim.setColor(rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.28)
            rim.setBin('fixed', int(look.get('binSort', 46)) - 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('splatPeak', 1.45))
            sec = float(look.get('splatSec', 0.15))
            peakA = float(look.get('peakAlpha', 0.92))
            return Parallel(
                Sequence(
                    LerpColorScaleInterval(
                        splat, sec * 0.25, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        splat, sec * 0.75, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(splat, sec, peak, blendType='easeOut'),
                Sequence(
                    LerpColorScaleInterval(
                        rim, sec * 0.2, Vec4(1, 1, 1, 0.65),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        rim, sec * 0.8, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(
                    rim, sec, peak * 1.12, blendType='easeOut'),
            )
        except Exception:
            return None

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Outward cream fleck — telegraph cream warn cousin (cheaper)."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + (0.18 * (index % 3))
            dist = float(look.get('fleckDist', 0.95)) * (
                0.6 + 0.14 * (index % 4))
            lift = float(look.get('fleckLift', 0.35)) * (
                0.45 + 0.16 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.09))
            if index % 2 == 0:
                cm = CardMaker(
                    'snare-string-counter-cream-splash-fleck-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.35, 0.35, 0.35)
                midScale = Point3(1.1, 1.1, 0.55)
                endScale = Point3(1.4, 1.4, 0.12)
            else:
                cm = CardMaker(
                    'snare-string-counter-cream-splash-streak-%s' % index)
                cm.setFrame(
                    -half * 0.32, half * 0.32, -half * 1.45, half * 1.45)
                startScale = Point3(0.28, 0.28, 0.6)
                midScale = Point3(0.5, 0.5, 1.3)
                endScale = Point3(1.15, 0.2, 0.14)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            colors = look.get('fleckColors') or getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_SPLASH_FLECK_COLORS',
                ((1.0, 0.97, 0.82, 0.9),))
            color = colors[index % len(colors)]
            fleck.setColor(color[0], color[1], color[2], color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 46)) + 1)
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
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_DELAY_SEC', 0.16))
        parts = []

        if getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_COUNT', 3)))
        streakCount = max(0, int(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_COUNT', 1)))
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
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_HALF', 0.42))
        startScale = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_START', 0.28))
        peakScale = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_PEAK', 1.4))
        sec = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_SEC', 0.28))
        peakA = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.2))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        try:
            cm = CardMaker('snare-string-counter-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            binSort = int(getattr(
                CorruptionGlobals, 'SNARE_STRING_COUNTER_CREAM_SPLASH_BIN', 46))
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
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_SIZE', 0.12))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.82))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.5
        else:
            size = float(getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_SIZE', 0.1))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.85))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.2
        drift = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_DRIFT', 0.55))
        fall = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_FALL', 0.42))
        sec = float(getattr(
            CorruptionGlobals,
            'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_SEC', 0.32))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'snare-string-counter-cream-aftershock-%s-%s' % (
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
                origin[0] + cos(angle) * 0.08,
                origin[1] + sin(angle) * 0.08,
                origin[2] + 0.02 * (index % 2))
            spark.setScale(0.26 + 0.06 * (index % 3))
            binSort = int(getattr(
                CorruptionGlobals, 'SNARE_STRING_COUNTER_CREAM_SPLASH_BIN', 46))
            spark.setBin('fixed', binSort)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            return None

        end = Point3(
            origin[0] + cos(angle) * drift * 0.55,
            origin[1] + sin(angle) * drift * 0.55,
            origin[2] - fall - 0.08 * (index % 3))
        peak = size * (1.15 + 0.08 * (index % 2))
        self._nodes.append(spark)
        stagger = 0.02 * (index % 3)
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
                        spark, max(0.01, sec * 0.4), peak,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        spark, max(0.01, sec * 0.6), 0.12,
                        blendType='easeIn'),
                ),
            ),
        )

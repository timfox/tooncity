"""Cream / pastel warn flecks + delayed cream aftershock at telegraph start.

Sunny Toontown cream chips that pop with the telegraph ink drip / silhouette
— warn readability contrast against dark ink, not another ink spray — then a
delayed cream aftershock settles downward (soft halo + residual flecks /
streaks). Composes lift with CorruptTelegraphInkFx.telegraphInkLook; aftershock
grammar matches hit-spark / perfect-dodge / hang cream aftershock.
CorruptTelegraphCreamSparkleFx layers rising cream sparkles from this warn
spray (silhouette cream sparkle grammar). CorruptTelegraphCreamWashFx layers
a soft cream wash pulse after the stack (silhouette / idle wash grammar).
Wired from DistributedCorruptToon.announceAttackTelegraph. Client only.
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

from toontown.corruption import CorruptionGlobals


def telegraphCreamWarnLook(archetype=None, finaleLook=None):
    """Resolve cream warn fleck tunables; compose lift with telegraph ink look."""
    look = dict(getattr(
        CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_LOOK', {}) or {})
    # Lazy import avoids circular load with CorruptTelegraphInkFx.
    try:
        from toontown.corruption.CorruptTelegraphInkFx import telegraphInkLook
        ink = telegraphInkLook(archetype, finaleLook=finaleLook)
        look.setdefault('lift', float(ink.get('lift', 2.15)))
    except Exception:
        look.setdefault('lift', 2.15)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_BIN', 43)))
    return look


class TelegraphCreamWarnFlecks(object):
    """Owns cream/pastel warn flecks + delayed cream aftershock at telegraph."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._haloNP = None

    def play(self, pos, archetype=None, finaleLook=None, parent=None):
        """Spawn cream warn flecks + delayed aftershock. Returns Sequence or None."""
        if not getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_ENABLED', True):
            return None
        self.clear()
        look = telegraphCreamWarnLook(archetype, finaleLook=finaleLook)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look.get('lift', 2.15)))

        count = max(0, int(look.get('fleckCount', 0)))
        if count <= 0:
            return None

        parts = []
        for i in range(count):
            part = self._spawnFleck(parentNP, origin, look, i, count)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        fleckParallel = Parallel(*parts)
        # Residual cream aftershock after the warn fleck spray settles.
        aftershock = self._buildAftershock(parentNP, origin)
        if aftershock is not None:
            self._ival = Sequence(
                Parallel(
                    fleckParallel,
                    aftershock,
                ),
                Func(self.clear),
                name='corruptTelegraphCreamWarn',
            )
        else:
            self._ival = Sequence(
                fleckParallel,
                Func(self.clear),
                name='corruptTelegraphCreamWarn',
            )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop flecks/aftershock and remove every cream node."""
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

    def _buildAftershock(self, parentNP, origin):
        """Delayed soft cream flecks (+ optional halo) after the warn pop."""
        if not getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_DELAY_SEC', 0.18))
        parts = []

        if getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_COUNT', 3)))
        streakCount = max(0, int(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_COUNT', 2)))
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
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_HALF', 0.48))
        startScale = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_START', 0.3))
        peakScale = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_PEAK', 1.55))
        sec = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_SEC', 0.32))
        peakA = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_PEAK_ALPHA', 0.26))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.96, 0.78, 1.0))
        try:
            cm = CardMaker('corrupt-telegraph-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            binSort = int(getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_BIN', 43))
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
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_SIZE', 0.16))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.85))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.55
        else:
            size = float(getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_SIZE', 0.11))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.88))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.22
        drift = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_DRIFT', 0.7))
        sec = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_SEC', 0.38))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'corrupt-telegraph-cream-aftershock-%s-%s' % (
                    nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -size * 0.35, size * 0.35,
                    -size * 1.15, size * 1.15)
            else:
                cm.setFrame(
                    -size, size, -size * 0.85, size * 0.85)
            spark = parentNP.attachNewNode(cm.generate())
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(r, g, b, 1)
            spark.setColorScale(r, g, b, 0)
            spark.setPos(
                origin[0] + cos(angle) * 0.1,
                origin[1] + sin(angle) * 0.1,
                origin[2] + 0.03 * (index % 2))
            spark.setScale(0.28 + 0.08 * (index % 3))
            binSort = int(getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_BIN', 43))
            spark.setBin('fixed', binSort)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            return None

        # Settle downward — residual cream, not the initial outward warn glitter.
        end = Point3(
            origin[0] + cos(angle) * drift * 0.55,
            origin[1] + sin(angle) * drift * 0.55,
            origin[2] - 0.5 - 0.1 * (index % 3))
        peak = size * (1.2 + 0.1 * (index % 2))
        self._nodes.append(spark)
        stagger = 0.02 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    spark, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    spark, sec * 0.28, peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(spark, sec * 0.72, end, blendType='easeIn'),
                LerpScaleInterval(
                    spark, sec * 0.72, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    spark, sec * 0.72, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Radial cream / pastel warn fleck — contrast to ink drip, not ink."""
        try:
            colors = look.get('fleckColors') or (
                getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.95),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals, 'TELEGRAPH_CREAM_WARN_END_COLORS', ()) or
                ((1.0, 0.92, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Offset phase from ink drips so cream reads as a second warn layer.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 0.55
                + (0.09 * (index % 3)))
            dist = float(look.get('fleckDist', 1.15)) * (
                0.72 + 0.14 * (index % 4))
            # Slight upward lift — warn chips float out, ink drips fall down.
            lift = float(look.get('fleckLift', 0.55)) * (
                0.55 + 0.2 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.12))
            # Alternate soft chips vs thin cream streaks (pastel, not ink).
            if index % 2 == 0:
                cm = CardMaker('corrupt-telegraph-cream-warn-%s' % index)
                cm.setFrame(-half, half, -half * 0.85, half * 0.85)
                startScale = Point3(0.35, 0.35, 0.35)
                midScale = Point3(1.15, 1.15, 0.5)
                endScale = Point3(1.55, 1.55, 0.1)
            else:
                cm = CardMaker('corrupt-telegraph-cream-warn-streak-%s' % index)
                cm.setFrame(
                    -half * 0.38, half * 0.38, -half * 1.45, half * 1.45)
                startScale = Point3(0.28, 0.28, 0.65)
                midScale = Point3(0.55, 0.55, 1.25)
                endScale = Point3(1.2, 0.2, 0.15)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so the warn spray isn't a flat cream plate.
            tint = 0.9 + 0.1 * ((index * 2) % 5) / 4.0
            fleck.setColor(
                min(1.5, color[0] * tint),
                min(1.5, color[1] * tint),
                min(1.5, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 43)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.24))
            delay = 0.01 * index
            er, eg, eb, ea = endColor
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.4, midScale),
                        LerpScaleInterval(fleck, travel * 0.6, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

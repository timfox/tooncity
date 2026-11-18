"""Rising cream / pastel sparkle flecks on CorruptToon telegraph cream warn.

Sunny Toontown cream chips that rise from the telegraph cream warn fleck
origin — purity sparkle contrast, not another ink spray. Composes lift with
CorruptTelegraphCreamWarnFx.telegraphCreamWarnLook (#102) and borrows
rising / twinkle size/timing from
CorruptSilhouetteCreamSparkleFx.silhouetteCreamSparkleLook (#131) so telegraph
rising sparkles sit beside warn flecks + delayed aftershock without reading as
another outward warn spray. Wired from DistributedCorruptToon beside
TelegraphCreamWarnFlecks (play / clear together). Client only. Toontown
spiritual sequel — no keyblades / no KH branding.
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


def telegraphCreamSparkleLook(archetype=None, finaleLook=None):
    """Resolve rising telegraph-sparkle tunables; compose with warn + rim sparkle."""
    look = dict(getattr(
        CorruptionGlobals, 'TELEGRAPH_CREAM_SPARKLE_LOOK', {}) or {})
    # Lazy import avoids circular load with CorruptTelegraphCreamWarnFx.
    try:
        from toontown.corruption.CorruptTelegraphCreamWarnFx import (
            telegraphCreamWarnLook)
        warn = telegraphCreamWarnLook(archetype, finaleLook=finaleLook)
        look.setdefault('lift', float(warn.get('lift', 2.15)))
        # Start near the warn fleck spray radius (not a full outward glitter).
        look.setdefault(
            'warnRadius', float(warn.get('fleckDist', 1.15)) * float(
                look.get('warnRadiusScale', 0.42)))
        look.setdefault(
            'warnZJitter', float(warn.get('fleckLift', 0.55)) * float(
                look.get('warnZJitterScale', 0.35)))
    except Exception:
        look.setdefault('lift', 2.15)
        look.setdefault('warnRadius', 0.48)
        look.setdefault('warnZJitter', 0.19)
    # Prefer silhouette cream sparkle rising / twinkle grammar when unset.
    try:
        from toontown.corruption.CorruptSilhouetteCreamSparkleFx import (
            silhouetteCreamSparkleLook)
        sparkle = silhouetteCreamSparkleLook(archetype, finaleLook=finaleLook)
        look.setdefault(
            'fleckHalf', float(sparkle.get('fleckHalf', 0.06)) * float(
                look.get('fleckHalfScale', 1.05)))
        look.setdefault(
            'fleckSec', float(sparkle.get('fleckSec', 0.4)) * float(
                look.get('fleckSecScale', 0.92)))
        look.setdefault(
            'fleckLift', float(sparkle.get('fleckLift', 0.55)) * float(
                look.get('fleckLiftScale', 1.08)))
        look.setdefault(
            'fleckDist', float(sparkle.get('fleckDist', 0.12)) * float(
                look.get('fleckDistScale', 1.15)))
        look.setdefault(
            'fleckStagger', float(sparkle.get('fleckStagger', 0.038)))
    except Exception:
        look.setdefault('fleckHalf', 0.065)
        look.setdefault('fleckSec', 0.37)
        look.setdefault('fleckLift', 0.6)
        look.setdefault('fleckDist', 0.14)
        look.setdefault('fleckStagger', 0.038)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_SPARKLE_BIN', 44)))
    return look


class TelegraphCreamSparkles(object):
    """Owns a brief rising cream sparkle spray at telegraph cream warn."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, archetype=None, finaleLook=None, parent=None):
        """Spawn rising cream sparkles at `pos` (render space). Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_SPARKLE_ENABLED', True):
            return None
        self.clear()
        look = telegraphCreamSparkleLook(archetype, finaleLook=finaleLook)
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

        # Slight delay so rising sparkles read after the initial warn pop.
        delay = max(0.0, float(look.get('startDelaySec', 0.04)))
        self._ival = Sequence(
            Wait(delay),
            Parallel(*parts),
            Func(self.clear),
            name='corruptTelegraphCreamSparkle',
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
        for np in list(self._nodes):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Soft cream / pastel sparkle — starts near warn spray, rises (not outward glitter)."""
        try:
            colors = look.get('fleckColors') or (
                getattr(
                    CorruptionGlobals, 'TELEGRAPH_CREAM_SPARKLE_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.88),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals,
                    'TELEGRAPH_CREAM_SPARKLE_END_COLORS', ()) or
                ((1.0, 0.94, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Phase-offset from warn flecks (+0.55) and silhouette rim sparkle
            # (+0.95+1.35) so rising telegraph chips read as a distinct layer.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 0.55
                + 1.75
                + (0.17 * (index % 3)))
            rim = float(look.get('warnRadius', 0.48)) * (
                0.78 + 0.14 * (index % 4))
            start = Point3(
                origin[0] + sin(angle) * rim,
                origin[1] + cos(angle) * rim * 0.55,
                origin[2] + float(look.get('warnZJitter', 0.19)) * (
                    -0.15 + 0.28 * (index % 3)),
            )
            # Mostly rise — tiny outward so motion reads vertical, not warn spray.
            out = float(look.get('fleckDist', 0.14)) * (
                0.35 + 0.2 * (index % 3))
            lift = float(look.get('fleckLift', 0.6)) * (
                0.65 + 0.28 * (index % 3))
            end = Point3(
                start[0] + sin(angle) * out,
                start[1] + cos(angle) * out * 0.45,
                start[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.065))
            # Silhouette cream sparkle grammar: soft chips vs thin pastel streaks.
            if index % 2 == 0:
                cm = CardMaker('corrupt-telegraph-cream-sparkle-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.2, 0.2, 0.26)
                midScale = Point3(1.1, 1.1, 0.75)
                endScale = Point3(1.5, 1.5, 0.08)
            else:
                cm = CardMaker(
                    'corrupt-telegraph-cream-sparkle-streak-%s' % index)
                cm.setFrame(
                    -half * 0.26, half * 0.26, -half * 1.45, half * 1.45)
                startScale = Point3(0.18, 0.18, 0.4)
                midScale = Point3(0.5, 0.5, 1.2)
                endScale = Point3(1.05, 0.16, 0.08)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(start)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so rising sparkles aren't a flat cream plate.
            tint = 0.92 + 0.08 * ((index * 7) % 5) / 4.0
            fleck.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 44)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.37))
            delay = float(look.get('fleckStagger', 0.038)) * index
            er, eg, eb, ea = endColor
            # Twinkle: pop scale mid-way (sparkle) then fade while rising.
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.32, midScale),
                        LerpScaleInterval(fleck, travel * 0.68, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

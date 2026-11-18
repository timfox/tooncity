"""Rising cream / pastel sparkle flecks on CorruptToon death cream flecks.

Sunny Toontown cream chips that rise from the death cream fleck burst —
purity sparkle contrast, not another ink spray. Composes lift / burst
radius with CorruptDeathCreamFleckFx.deathCreamFleckLook (#94) and borrows
rising / twinkle size/timing from
CorruptSilhouetteCreamSparkleFx.silhouetteCreamSparkleLook (#131) /
CorruptTelegraphCreamSparkleFx.telegraphCreamSparkleLook (#135) so death
rising sparkles sit beside outward flecks + soft cream wash (#119) without
reading as another radial fleck spray. Wired from DeathPopSplat.play beside
DeathCreamFleckBurst + DeathCreamWashPulse. Client only. Toontown spiritual
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


def deathCreamSparkleLook(archetype=None, finaleLook=None):
    """Resolve rising death-sparkle tunables; compose with fleck + rim sparkle."""
    look = dict(getattr(
        CorruptionGlobals, 'DEATH_CREAM_SPARKLE_LOOK', {}) or {})
    # Lazy import avoids circular load with CorruptDeathCreamFleckFx.
    try:
        from toontown.corruption.CorruptDeathCreamFleckFx import (
            deathCreamFleckLook)
        fleck = deathCreamFleckLook(archetype)
        look.setdefault('lift', float(fleck.get('lift', 1.35)))
        # Start near the outward fleck spray radius (not a full radial glitter).
        look.setdefault(
            'burstRadius', float(fleck.get('fleckDist', 2.05)) * float(
                look.get('burstRadiusScale', 0.28)))
        look.setdefault(
            'burstZJitter', float(fleck.get('fleckLift', 1.35)) * float(
                look.get('burstZJitterScale', 0.22)))
    except Exception:
        look.setdefault('lift', 1.35)
        look.setdefault('burstRadius', 0.57)
        look.setdefault('burstZJitter', 0.3)
    # Prefer telegraph / silhouette cream sparkle rising / twinkle grammar.
    try:
        from toontown.corruption.CorruptTelegraphCreamSparkleFx import (
            telegraphCreamSparkleLook)
        sparkle = telegraphCreamSparkleLook(archetype, finaleLook=finaleLook)
        look.setdefault(
            'fleckHalf', float(sparkle.get('fleckHalf', 0.065)) * float(
                look.get('fleckHalfScale', 1.08)))
        look.setdefault(
            'fleckSec', float(sparkle.get('fleckSec', 0.37)) * float(
                look.get('fleckSecScale', 1.05)))
        look.setdefault(
            'fleckLift', float(sparkle.get('fleckLift', 0.6)) * float(
                look.get('fleckLiftScale', 1.15)))
        look.setdefault(
            'fleckDist', float(sparkle.get('fleckDist', 0.14)) * float(
                look.get('fleckDistScale', 1.2)))
        look.setdefault(
            'fleckStagger', float(sparkle.get('fleckStagger', 0.038)))
        look.setdefault(
            'startDelaySec', float(sparkle.get('startDelaySec', 0.04)) + float(
                look.get('startDelayBias', 0.04)))
    except Exception:
        try:
            from toontown.corruption.CorruptSilhouetteCreamSparkleFx import (
                silhouetteCreamSparkleLook)
            sparkle = silhouetteCreamSparkleLook(
                archetype, finaleLook=finaleLook)
            look.setdefault(
                'fleckHalf', float(sparkle.get('fleckHalf', 0.06)) * float(
                    look.get('fleckHalfScale', 1.08)))
            look.setdefault(
                'fleckSec', float(sparkle.get('fleckSec', 0.4)) * float(
                    look.get('fleckSecScale', 1.05)))
            look.setdefault(
                'fleckLift', float(sparkle.get('fleckLift', 0.55)) * float(
                    look.get('fleckLiftScale', 1.15)))
            look.setdefault(
                'fleckDist', float(sparkle.get('fleckDist', 0.12)) * float(
                    look.get('fleckDistScale', 1.2)))
            look.setdefault(
                'fleckStagger', float(sparkle.get('fleckStagger', 0.038)))
        except Exception:
            look.setdefault('fleckHalf', 0.07)
            look.setdefault('fleckSec', 0.39)
            look.setdefault('fleckLift', 0.69)
            look.setdefault('fleckDist', 0.17)
            look.setdefault('fleckStagger', 0.038)
        look.setdefault('startDelaySec', 0.08)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'DEATH_CREAM_SPARKLE_BIN', 48)))
    return look


class DeathCreamSparkles(object):
    """Owns a brief rising cream sparkle spray at death cream fleck burst."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, archetype=None, finaleLook=None, parent=None):
        """Spawn rising cream sparkles at `pos` (render space). Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals, 'DEATH_CREAM_SPARKLE_ENABLED', True):
            return None
        self.clear()
        look = deathCreamSparkleLook(archetype, finaleLook=finaleLook)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look.get('lift', 1.35)))

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

        # Slight delay so rising sparkles read after the outward fleck pop.
        delay = max(0.0, float(look.get('startDelaySec', 0.08)))
        self._ival = Sequence(
            Wait(delay),
            Parallel(*parts),
            Func(self.clear),
            name='corruptDeathCreamSparkle',
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
        """Soft cream / pastel sparkle — starts near fleck burst, rises (not radial glitter)."""
        try:
            colors = look.get('fleckColors') or (
                getattr(
                    CorruptionGlobals, 'DEATH_CREAM_SPARKLE_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.88),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals,
                    'DEATH_CREAM_SPARKLE_END_COLORS', ()) or
                ((1.0, 0.94, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Phase-offset from death flecks (+0.35) and telegraph sparkle
            # (+0.55+1.75) so rising death chips read as a distinct layer.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 0.35
                + 2.05
                + (0.16 * (index % 3)))
            rim = float(look.get('burstRadius', 0.57)) * (
                0.78 + 0.14 * (index % 4))
            start = Point3(
                origin[0] + sin(angle) * rim,
                origin[1] + cos(angle) * rim * 0.55,
                origin[2] + float(look.get('burstZJitter', 0.3)) * (
                    -0.12 + 0.26 * (index % 3)),
            )
            # Mostly rise — tiny outward so motion reads vertical, not fleck spray.
            out = float(look.get('fleckDist', 0.17)) * (
                0.35 + 0.2 * (index % 3))
            lift = float(look.get('fleckLift', 0.69)) * (
                0.65 + 0.28 * (index % 3))
            end = Point3(
                start[0] + sin(angle) * out,
                start[1] + cos(angle) * out * 0.45,
                start[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.07))
            # Telegraph / silhouette cream sparkle grammar: soft chips vs streaks.
            if index % 2 == 0:
                cm = CardMaker('corrupt-death-cream-sparkle-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.2, 0.2, 0.26)
                midScale = Point3(1.1, 1.1, 0.75)
                endScale = Point3(1.5, 1.5, 0.08)
            else:
                cm = CardMaker(
                    'corrupt-death-cream-sparkle-streak-%s' % index)
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
            fleck.setBin('fixed', int(look.get('binSort', 48)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.39))
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

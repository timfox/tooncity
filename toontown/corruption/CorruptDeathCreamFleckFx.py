"""Rubber-hose cream / pastel fleck burst layered on CorruptDeathPopFx.

Sunny Toontown cream chips that pop with the defeat ink splat — purity flecks,
not ink. Composes lift / origin with CorruptDeathPopFx.deathPopLook so the
burst sits on the same death pop. Wired from DeathPopSplat.play. Client only.
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


def deathCreamFleckLook(archetype=None):
    """Resolve cream fleck tunables; compose lift with death-pop look."""
    look = dict(getattr(
        CorruptionGlobals, 'DEATH_CREAM_FLECK_LOOK', {}) or {})
    # Lazy import avoids circular load with CorruptDeathPopFx.
    try:
        from toontown.corruption.CorruptDeathPopFx import deathPopLook
        death = deathPopLook(archetype)
        look.setdefault('lift', float(death.get('lift', 1.35)))
    except Exception:
        look.setdefault('lift', 1.35)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'DEATH_CREAM_FLECK_BIN', 47)))
    return look


class DeathCreamFleckBurst(object):
    """Owns a brief cream/pastel fleck spray at a world death-pop position."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, archetype=None, parent=None):
        """Spawn cream flecks at `pos` (render space). Returns Sequence or None."""
        if not getattr(CorruptionGlobals, 'DEATH_CREAM_FLECK_ENABLED', True):
            return None
        self.clear()
        look = deathCreamFleckLook(archetype)
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

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='corruptDeathCreamFleck',
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
        """Radial cream / pastel fleck — sunny purity chip, not ink."""
        try:
            colors = look.get('fleckColors') or (
                getattr(CorruptionGlobals, 'DEATH_CREAM_FLECK_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.95),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals, 'DEATH_CREAM_FLECK_END_COLORS', ()) or
                ((1.0, 0.92, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Offset phase from ink droplets so cream reads as a second layer.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 0.35
                + (0.11 * (index % 3)))
            dist = float(look.get('fleckDist', 2.05)) * (
                0.68 + 0.16 * (index % 4))
            lift = float(look.get('fleckLift', 1.35)) * (
                0.6 + 0.18 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.18))
            # Alternate soft chips vs thin cream streaks (pastel, not ink).
            if index % 2 == 0:
                cm = CardMaker('corrupt-death-cream-fleck-%s' % index)
                cm.setFrame(-half, half, -half * 0.85, half * 0.85)
                startScale = Point3(0.4, 0.4, 0.4)
                midScale = Point3(1.25, 1.25, 0.55)
                endScale = Point3(1.7, 1.7, 0.12)
            else:
                cm = CardMaker('corrupt-death-cream-streak-%s' % index)
                cm.setFrame(
                    -half * 0.38, half * 0.38, -half * 1.55, half * 1.55)
                startScale = Point3(0.32, 0.32, 0.7)
                midScale = Point3(0.65, 0.65, 1.45)
                endScale = Point3(1.35, 0.22, 0.18)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so the burst isn't a flat cream plate.
            tint = 0.9 + 0.1 * ((index * 2) % 5) / 4.0
            fleck.setColor(
                min(1.5, color[0] * tint),
                min(1.5, color[1] * tint),
                min(1.5, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 47)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.32))
            delay = 0.012 * index
            er, eg, eb, ea = endColor
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.42, midScale),
                        LerpScaleInterval(fleck, travel * 0.58, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

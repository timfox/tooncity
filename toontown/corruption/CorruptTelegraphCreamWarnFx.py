"""Cream / pastel warn flecks at CorruptToon attack telegraph start.

Sunny Toontown cream chips that pop with the telegraph ink drip / silhouette
— warn readability contrast against dark ink, not another ink spray. Composes
lift with CorruptTelegraphInkFx.telegraphInkLook. Wired from
DistributedCorruptToon.announceAttackTelegraph. Client only. Toontown
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
    """Owns a brief cream/pastel warn fleck spray at telegraph start."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, archetype=None, finaleLook=None, parent=None):
        """Spawn cream warn flecks at `pos` (render space). Returns Sequence or None."""
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

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='corruptTelegraphCreamWarn',
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

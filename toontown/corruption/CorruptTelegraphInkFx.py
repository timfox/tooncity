"""Short rubber-hose ink drip / splat pop on CorruptToon attack telegraph.

World-space CardMaker juice wired from DistributedCorruptToon.announceAttackTelegraph
so wind-ups read as ink charging — drip falls + tiny chest splat, not a defeat
burst. Archetype palette (purple / sludge green / amber). Toontown spiritual
sequel only — no keyblades / no KH framing.
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


def telegraphInkLook(archetype, finaleLook=None):
    """Resolve drip palette for archetype; finale look can override colors."""
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = CorruptionGlobals.ARCHETYPE_INK
    looks = CorruptionGlobals.TELEGRAPH_INK_DRIP_LOOK
    look = dict(looks.get(aid, looks[CorruptionGlobals.ARCHETYPE_INK]))
    if finaleLook:
        # Tint splat/drip toward Overlord charge colors so P1/P2 still read.
        charge = finaleLook.get('telegraphCharge')
        if charge and len(charge) >= 3:
            look['splatColor'] = (
                min(1.2, charge[0] * 0.45),
                min(1.2, charge[1] * 0.45),
                min(1.2, charge[2] * 0.45),
                0.92,
            )
            look['dripColor'] = (
                min(1.1, charge[0] * 0.35),
                min(1.1, charge[1] * 0.35),
                min(1.1, charge[2] * 0.35),
                0.95,
            )
            look['streakColor'] = (
                min(1.3, charge[0] * 0.5),
                min(1.3, charge[1] * 0.5),
                min(1.3, charge[2] * 0.5),
                0.9,
            )
    return look


class TelegraphInkDrip(object):
    """Owns the brief telegraph ink drip + splat pop at a world position."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, archetype=None, finaleLook=None, parent=None):
        """Spawn drip/splat at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = telegraphInkLook(archetype, finaleLook=finaleLook)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look['lift']))

        parts = []
        splat = self._spawnSplat(parentNP, origin, look)
        if splat is not None:
            parts.append(splat)

        count = int(look['dripCount'])
        for i in range(count):
            part = self._spawnDrip(parentNP, origin, look, i, count)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='corruptTelegraphInkDrip',
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
        for np in self._nodes:
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _spawnSplat(self, parentNP, origin, look):
        """Tiny billboard splat that pops then fades — telegraph readability cue."""
        try:
            half = float(look['splatHalf'])
            cm = CardMaker('corrupt-telegraph-ink-splat')
            cm.setFrame(-half, half, -half, half)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look['splatColor']
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0.95)
            splat.setScale(0.25)
            splat.setBin('fixed', 41)
            splat.setDepthWrite(False)
            self._nodes.append(splat)
            peak = float(look['splatPeak'])
            sec = float(look['splatSec'])
            return Sequence(
                Parallel(
                    LerpScaleInterval(
                        splat, sec * 0.45, peak, blendType='easeOut'),
                    LerpColorScaleInterval(
                        splat, sec * 0.45, Vec4(1.15, 1.15, 1.15, 1.0)),
                ),
                Parallel(
                    LerpScaleInterval(
                        splat, sec * 0.55, peak * 1.15, blendType='easeIn'),
                    LerpColorScaleInterval(
                        splat, sec * 0.55, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _spawnDrip(self, parentNP, origin, look, index, count):
        """Rubber-hose ink drip falling downward from the telegraph origin."""
        try:
            # Fan slightly sideways; gravity is the main motion (drip, not spray).
            angle = (2.0 * pi * index) / max(1, count) + 0.35
            spread = float(look['dripSpread']) * (0.35 + 0.22 * (index % 3))
            fall = float(look['dripFall']) * (0.75 + 0.12 * (index % 4))
            end = Point3(
                origin[0] + sin(angle) * spread,
                origin[1] + cos(angle) * spread * 0.55,
                origin[2] - fall,
            )
            half = float(look['dripHalf'])
            # Alternate fat drops vs long streaks for hose variety.
            if index % 2 == 0:
                cm = CardMaker('corrupt-telegraph-drip-%s' % index)
                cm.setFrame(-half, half, -half * 1.35, half * 1.35)
                startScale = Point3(0.55, 0.55, 0.7)
                midScale = Point3(0.85, 0.85, 1.45)
                endScale = Point3(1.35, 1.35, 0.25)
                color = look['dripColor']
            else:
                cm = CardMaker('corrupt-telegraph-streak-%s' % index)
                cm.setFrame(-half * 0.35, half * 0.35, -half * 2.1, half * 2.1)
                startScale = Point3(0.4, 0.4, 0.85)
                midScale = Point3(0.55, 0.55, 1.75)
                endScale = Point3(1.15, 0.3, 0.2)
                color = look['streakColor']
            drip = parentNP.attachNewNode(cm.generate())
            # Stagger start a hair so drips don't look cloned.
            start = Point3(
                origin[0] + sin(angle) * spread * 0.15,
                origin[1] + cos(angle) * spread * 0.1,
                origin[2] - 0.08 * index,
            )
            drip.setPos(start)
            drip.setBillboardPointEye()
            drip.setTransparency(TransparencyAttrib.MAlpha)
            tint = 0.88 + 0.1 * ((index * 2) % 5) / 4.0
            drip.setColor(
                min(1.4, color[0] * tint),
                min(1.4, color[1] * tint),
                min(1.4, color[2] * tint),
                color[3])
            drip.setScale(startScale)
            drip.setBin('fixed', 42)
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look['dripSec'])
            delay = 0.02 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(drip, travel, end, blendType='easeIn'),
                    Sequence(
                        LerpScaleInterval(drip, travel * 0.4, midScale),
                        LerpScaleInterval(drip, travel * 0.6, endScale),
                    ),
                    LerpColorScaleInterval(
                        drip, travel, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            return None

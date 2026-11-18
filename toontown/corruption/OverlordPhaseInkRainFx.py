"""Rubber-hose ink rain / ink fall on Ink Overlord phase telegraphs.

World-space CardMaker shower that falls from above the boss when a finale
phase look is active — denser and taller than street CorruptTelegraphInkFx
drips, cheaper than full-screen campaign stings. Wired beside
OverlordTelegraphCrownFx from DistributedCorruptToon.announceAttackTelegraph.
Phase charge colors tint the fall (magenta rise / crimson unleash).
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


def overlordInkRainLook(finaleLook=None, phase=1):
    """Resolve ink-rain palette / density; phase charge colors tint the fall."""
    look = dict(CorruptionGlobals.OVERLORD_PHASE_INK_RAIN_LOOK)
    try:
        phaseIndex = max(1, int(phase))
    except (TypeError, ValueError):
        phaseIndex = 1
    # P2 unleashed rains harder / falls farther so the phase flip still reads.
    if phaseIndex >= 2:
        look['dropCount'] = int(look.get('dropCount', 7)) + 2
        look['lift'] = float(look.get('lift', 5.4)) + 0.45
        look['fall'] = float(look.get('fall', 4.2)) + 0.55
        look['spread'] = float(look.get('spread', 1.55)) * 1.12
        look['peakAlpha'] = min(
            1.0, float(look.get('peakAlpha', 0.92)) * 1.05)
    if finaleLook:
        charge = finaleLook.get('telegraphCharge')
        if charge and len(charge) >= 3:
            look['dropColor'] = (
                min(1.25, charge[0] * 0.42),
                min(1.25, charge[1] * 0.42),
                min(1.25, charge[2] * 0.42),
                float(look.get('dropColor', (0, 0, 0, 0.92))[3]),
            )
            look['streakColor'] = (
                min(1.4, charge[0] * 0.55),
                min(1.4, charge[1] * 0.55),
                min(1.4, charge[2] * 0.55),
                float(look.get('streakColor', (0, 0, 0, 0.88))[3]),
            )
            look['puddleColor'] = (
                min(1.15, charge[0] * 0.32),
                min(1.15, charge[1] * 0.32),
                min(1.15, charge[2] * 0.32),
                float(look.get('puddleColor', (0, 0, 0, 0.7))[3]),
            )
    return look


class OverlordPhaseInkRain(object):
    """Owns the brief ink rain / ink fall shower above the Overlord."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, finaleLook=None, phase=1, parent=None):
        """Spawn ink rain at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = overlordInkRainLook(finaleLook=finaleLook, phase=phase)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(
                pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look['lift']))

        parts = []
        puddle = self._spawnPuddle(parentNP, pos, look)
        if puddle is not None:
            parts.append(puddle)

        count = max(3, int(look.get('dropCount', 7)))
        for i in range(count):
            part = self._spawnDrop(parentNP, origin, look, i, count)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='overlordPhaseInkRain',
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

    def _spawnPuddle(self, parentNP, bossPos, look):
        """Soft ground ink puddle that blooms as rain lands — phase readability."""
        try:
            half = float(look.get('puddleHalf', 0.55))
            cm = CardMaker('overlord-ink-rain-puddle')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            puddle = parentNP.attachNewNode(cm.generate())
            lift = float(look.get('puddleLift', 0.08))
            puddle.setPos(bossPos[0], bossPos[1], bossPos[2] + lift)
            puddle.setP(-90)
            puddle.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get('puddleColor', (0.12, 0.04, 0.18, 0.7))
            puddle.setColor(color[0], color[1], color[2], color[3])
            puddle.setColorScale(1, 1, 1, 0)
            puddle.setScale(0.35)
            puddle.setBin('fixed', int(look.get('binSort', 43)) - 1)
            puddle.setDepthWrite(False)
            self._nodes.append(puddle)
            peak = float(look.get('puddlePeak', 2.4))
            fadeIn = float(look.get('puddleInSec', 0.18))
            hold = float(look.get('puddleHoldSec', 0.12))
            fadeOut = float(look.get('puddleOutSec', 0.28))
            peakA = float(look.get('peakAlpha', 0.92)) * 0.75
            return Sequence(
                Wait(float(look.get('puddleDelay', 0.16))),
                Parallel(
                    LerpScaleInterval(
                        puddle, fadeIn, peak, blendType='easeOut'),
                    LerpColorScaleInterval(
                        puddle, fadeIn, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                ),
                Wait(hold),
                Parallel(
                    LerpScaleInterval(
                        puddle, fadeOut, peak * 1.2, blendType='easeIn'),
                    LerpColorScaleInterval(
                        puddle, fadeOut, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _spawnDrop(self, parentNP, origin, look, index, count):
        """One rubber-hose ink drop / streak falling from above the boss."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + 0.22
            # Slight radial jitter so the shower doesn't look cloned.
            spread = float(look['spread']) * (0.28 + 0.18 * (index % 5))
            fall = float(look['fall']) * (0.78 + 0.08 * (index % 4))
            end = Point3(
                origin[0] + sin(angle) * spread,
                origin[1] + cos(angle) * spread * 0.55,
                origin[2] - fall,
            )
            half = float(look['dropHalf'])
            # Alternate fat drops vs long ink streaks for hose variety.
            if index % 2 == 0:
                cm = CardMaker('overlord-ink-rain-drop-%s' % index)
                cm.setFrame(-half, half, -half * 1.45, half * 1.45)
                startScale = Point3(0.5, 0.5, 0.65)
                midScale = Point3(0.75, 0.75, 1.55)
                endScale = Point3(1.25, 1.25, 0.22)
                color = look['dropColor']
            else:
                cm = CardMaker('overlord-ink-rain-streak-%s' % index)
                cm.setFrame(-half * 0.28, half * 0.28, -half * 2.4, half * 2.4)
                startScale = Point3(0.35, 0.35, 0.9)
                midScale = Point3(0.5, 0.5, 1.95)
                endScale = Point3(1.05, 0.25, 0.18)
                color = look['streakColor']
            drip = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + sin(angle) * spread * 0.2,
                origin[1] + cos(angle) * spread * 0.12,
                origin[2] + 0.12 * (index % 3),
            )
            drip.setPos(start)
            drip.setBillboardPointEye()
            drip.setTransparency(TransparencyAttrib.MAlpha)
            tint = 0.88 + 0.1 * ((index * 3) % 5) / 4.0
            drip.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            drip.setScale(startScale)
            drip.setBin('fixed', int(look.get('binSort', 43)))
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look['fallSec'])
            delay = float(look.get('staggerSec', 0.03)) * index
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

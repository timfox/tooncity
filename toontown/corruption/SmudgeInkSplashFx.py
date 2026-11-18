"""Rubber-hose purple ink splash when Ink Smudge takes a hit or dies.

Cheap world-space CardMaker juice for swarm readability — which Smudge got
tagged / popped stays scannable in a pack. Composes palette / motion cues
from SmudgeInkTelegraphFx (purple fist/smear), CorruptDeathPopFx (radial
flecks), and IdleInkDripFx (soft falling drip). Hit path also arms
SmudgeHitCreamSplashFx (cream splash + delayed cream aftershock — sunny
cream/pastel juice against purple ink; Brute spit / Gunk puddle / Snare
counter cream-splash grammar) and SmudgeHitCreamWashFx (soft cream wash
pulse — cream/pastel contrast against purple ink; overlord-hit / telegraph /
silhouette / death cream-wash grammar). Wired from DistributedCorruptToon
hit reaction + announceDefeat for ARCHETYPE_INK only. Toontown spiritual
sequel only — no keyblades / no KH branding.
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
from toontown.corruption.CorruptDeathPopFx import deathPopLook
from toontown.corruption.IdleInkDripFx import idleInkLook
from toontown.corruption.SmudgeInkTelegraphFx import smudgeTelegraphInkLook


def smudgeInkSplashLook(kind='hit'):
    """Resolve splash palette / motion; compose with telegraph / death / idle."""
    key = 'death' if str(kind).lower() == 'death' else 'hit'
    looks = CorruptionGlobals.SMUDGE_INK_SPLASH_LOOK
    look = dict(looks.get(key, looks['hit']))

    fist = smudgeTelegraphInkLook()
    death = deathPopLook(CorruptionGlobals.ARCHETYPE_INK)
    idle = idleInkLook(CorruptionGlobals.ARCHETYPE_INK)

    # Prefer explicit tunables; fall back to composed sibling FX colors.
    look.setdefault('splatColor', fist.get('fistColor', (0.55, 0.18, 0.95, 1.0)))
    look.setdefault('rimColor', fist.get('rimColor', (1.15, 0.45, 1.55, 1.0)))
    look.setdefault(
        'smearColor', fist.get('smearColor', (0.75, 0.28, 1.15, 0.9)))
    look.setdefault(
        'fleckColor', death.get('dropletColor', (0.42, 0.12, 0.62, 0.95)))
    look.setdefault(
        'dripColor', idle.get('dripColor', (0.32, 0.08, 0.48, 0.55)))
    look.setdefault(
        'streakColor', idle.get('streakColor', (0.48, 0.16, 0.72, 0.48)))
    return look


class SmudgeInkSplash(object):
    """Owns a brief purple ink splash at a world position (hit or death)."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, kind='hit', parent=None):
        """Spawn splash at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = smudgeInkSplashLook(kind)
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

        smearCount = max(0, int(look.get('smearCount', 0)))
        for i in range(smearCount):
            part = self._spawnSmear(parentNP, origin, look, i)
            if part is not None:
                parts.append(part)

        fleckCount = max(0, int(look.get('fleckCount', 0)))
        for i in range(fleckCount):
            part = self._spawnFleck(parentNP, origin, look, i, fleckCount)
            if part is not None:
                parts.append(part)

        dripCount = max(0, int(look.get('dripCount', 0)))
        for i in range(dripCount):
            part = self._spawnDrip(parentNP, origin, look, i)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='smudgeInkSplash-%s' % look.get('id', kind),
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
        """Tiny billboard ink blob — smack / pop readability core."""
        try:
            half = float(look.get('splatHalf', 0.28))
            cm = CardMaker('smudge-ink-splash-core')
            cm.setFrame(-half, half, -half * 0.92, half * 0.92)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look['splatColor']
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0)
            splat.setScale(0.35)
            splat.setBin('fixed', int(look.get('binSort', 44)))
            splat.setDepthWrite(False)
            self._nodes.append(splat)

            # Hot rim so the smack reads against Loopy purple fog.
            rimHalf = half * float(look.get('rimScale', 1.28))
            cmRim = CardMaker('smudge-ink-splash-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.9)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin)
            rim.setBillboardPointEye()
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look['rimColor']
            rim.setColor(rimColor[0], rimColor[1], rimColor[2], 0.55)
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.3)
            rim.setBin('fixed', int(look.get('binSort', 44)) - 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('splatPeak', 1.65))
            sec = float(look.get('splatSec', 0.2))
            peakA = float(look.get('peakAlpha', 0.95))
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
                        rim, sec * 0.2, Vec4(1, 1, 1, 0.7),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        rim, sec * 0.8, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(
                    rim, sec, peak * 1.15, blendType='easeOut'),
            )
        except Exception:
            return None

    def _spawnSmear(self, parentNP, origin, look, index):
        """Radial purple smear — SmudgeInkTelegraphFx punch-smear cousin."""
        try:
            side = -1.0 if (index % 2) == 0 else 1.0
            t = 0.4 + 0.22 * (index // 2)
            angle = (pi * 0.4) + side * (0.32 + 0.18 * index)
            spread = float(look.get('smearSpread', 0.85))
            end = Point3(
                origin[0] + cos(angle) * spread * t,
                origin[1] + sin(angle) * spread * 0.5,
                origin[2] + 0.06 + sin(pi * 0.22 * index) * 0.22,
            )
            half = float(look.get('smearHalf', 0.1))
            cm = CardMaker('smudge-ink-splash-smear-%s' % index)
            cm.setFrame(-half, half, -half * 1.1, half * 1.1)
            smear = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + side * 0.05,
                origin[1] + 0.04,
                origin[2] + 0.04 * ((index % 3) - 1),
            )
            smear.setPos(start)
            smear.setBillboardPointEye()
            smear.setTransparency(TransparencyAttrib.MAlpha)
            color = look['smearColor']
            tint = 0.9 + 0.08 * (index % 3)
            smear.setColor(
                min(1.4, color[0] * tint),
                min(1.4, color[1] * tint),
                min(1.4, color[2] * tint),
                color[3])
            smear.setScale(Point3(0.5, 0.5, 0.65))
            smear.setBin('fixed', int(look.get('binSort', 44)) + 1)
            smear.setDepthWrite(False)
            self._nodes.append(smear)
            travel = float(look.get('smearSec', 0.22))
            delay = 0.012 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(smear, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(
                            smear, travel * 0.4, Point3(1.2, 0.7, 1.3),
                            blendType='easeOut'),
                        LerpScaleInterval(
                            smear, travel * 0.6, Point3(0.35, 0.25, 1.55),
                            blendType='easeIn'),
                    ),
                    LerpColorScaleInterval(
                        smear, travel, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Radial ink fleck — CorruptDeathPopFx droplet cousin (cheaper)."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + (0.15 * (index % 3))
            dist = float(look.get('fleckDist', 1.35)) * (0.65 + 0.16 * (index % 4))
            lift = float(look.get('fleckLift', 0.55)) * (0.5 + 0.18 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.14))
            if index % 2 == 0:
                cm = CardMaker('smudge-ink-splash-fleck-%s' % index)
                cm.setFrame(-half, half, -half, half)
                startScale = Point3(0.4, 0.4, 0.4)
                midScale = Point3(1.15, 1.15, 0.5)
                endScale = Point3(1.55, 1.55, 0.12)
            else:
                cm = CardMaker('smudge-ink-splash-streak-%s' % index)
                cm.setFrame(-half * 0.4, half * 0.4, -half * 1.45, half * 1.45)
                startScale = Point3(0.3, 0.3, 0.65)
                midScale = Point3(0.6, 0.6, 1.35)
                endScale = Point3(1.2, 0.22, 0.18)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            color = look['fleckColor']
            tint = 0.88 + 0.1 * ((index * 3) % 5) / 4.0
            fleck.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 44)) + 2)
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.26))
            delay = 0.012 * index
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

    def _spawnDrip(self, parentNP, origin, look, index):
        """Soft falling drip — IdleInkDripFx cousin for residual ink read."""
        try:
            angle = 0.9 + index * 1.1
            spread = float(look.get('dripSpread', 0.28)) * (0.45 + 0.15 * index)
            fall = float(look.get('dripFall', 0.85)) * (0.85 + 0.1 * index)
            end = Point3(
                origin[0] + sin(angle) * spread,
                origin[1] + cos(angle) * spread * 0.4,
                origin[2] - fall,
            )
            half = float(look.get('dripHalf', 0.09))
            if index % 2 == 0:
                cm = CardMaker('smudge-ink-splash-drip-%s' % index)
                cm.setFrame(-half, half, -half * 1.15, half * 1.15)
                startScale = Point3(0.4, 0.4, 0.5)
                midScale = Point3(0.6, 0.6, 1.05)
                endScale = Point3(0.95, 0.95, 0.18)
                color = look['dripColor']
            else:
                cm = CardMaker('smudge-ink-splash-drip-streak-%s' % index)
                cm.setFrame(-half * 0.28, half * 0.28, -half * 1.7, half * 1.7)
                startScale = Point3(0.3, 0.3, 0.65)
                midScale = Point3(0.4, 0.4, 1.25)
                endScale = Point3(0.8, 0.22, 0.14)
                color = look['streakColor']
            drip = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + sin(angle) * spread * 0.1,
                origin[1] + cos(angle) * spread * 0.06,
                origin[2] - 0.04 * index,
            )
            drip.setPos(start)
            drip.setBillboardPointEye()
            drip.setTransparency(TransparencyAttrib.MAlpha)
            drip.setColor(color[0], color[1], color[2], color[3])
            drip.setScale(startScale)
            drip.setBin('fixed', int(look.get('binSort', 44)) - 2)
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look.get('dripSec', 0.4))
            delay = float(look.get('dripStagger', 0.03)) * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(drip, travel, end, blendType='easeIn'),
                    Sequence(
                        LerpScaleInterval(drip, travel * 0.45, midScale),
                        LerpScaleInterval(drip, travel * 0.55, endScale),
                    ),
                    LerpColorScaleInterval(
                        drip, travel, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            return None

"""Rubber-hose magenta/crimson ink splash when Ink Overlord is hit or dies.

Cheap world-space CardMaker juice so tagged / popped Overlord stays scannable
as boss (not a street Smudge). Composes palette / motion cues from
OverlordTelegraphCrownFx (magenta rim/flash), OverlordPhaseInkRainFx (ink
streaks), CorruptDeathPopFx (radial flecks), and IdleInkDripFx (soft falling
drip). Phase charge retints P1 magenta swell vs P2 crimson fury. Hit path
also arms OverlordHitCreamWashFx (soft cream wash pulse — cream/pastel
contrast against magenta ink; telegraph / silhouette / death cream-wash
grammar). Wired from DistributedCorruptToon hit reaction + announceDefeat
when a finale phase look is active. Toontown spiritual sequel only — no
keyblades / no KH branding.
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
from toontown.corruption.OverlordPhaseInkRainFx import overlordInkRainLook
from toontown.corruption.OverlordTelegraphCrownFx import overlordCrownLook


def overlordMagentaInkSplashLook(kind='hit', finaleLook=None, phase=1):
    """Resolve splash palette / motion; compose with crown / rain / death / idle."""
    key = 'death' if str(kind).lower() == 'death' else 'hit'
    looks = CorruptionGlobals.OVERLORD_MAGENTA_INK_SPLASH_LOOK
    look = dict(looks.get(key, looks['hit']))

    crown = overlordCrownLook(finaleLook=finaleLook, phase=phase)
    rain = overlordInkRainLook(finaleLook=finaleLook, phase=phase)
    death = deathPopLook(CorruptionGlobals.ARCHETYPE_INK)
    idle = idleInkLook(CorruptionGlobals.ARCHETYPE_INK, finaleLook=finaleLook)

    # Prefer explicit tunables; fall back to composed sibling FX colors.
    look.setdefault(
        'splatColor', crown.get('flashColor', (1.15, 0.45, 1.25, 1.0)))
    look.setdefault(
        'rimColor', crown.get('rimColor', (0.85, 0.25, 0.95, 1.0)))
    look.setdefault(
        'smearColor', rain.get('streakColor', (0.55, 0.18, 0.78, 0.88)))
    look.setdefault(
        'fleckColor', death.get('dropletColor', (0.42, 0.12, 0.62, 0.95)))
    look.setdefault(
        'dripColor', idle.get('dripColor', rain.get(
            'dropColor', (0.28, 0.08, 0.42, 0.92))))
    look.setdefault(
        'streakColor', idle.get('streakColor', rain.get(
            'streakColor', (0.55, 0.18, 0.78, 0.88))))

    # Phase charge retint so P1 magenta vs P2 crimson sticks on hit/death.
    if finaleLook:
        charge = finaleLook.get('telegraphCharge')
        if charge and len(charge) >= 3:
            look['splatColor'] = (
                min(1.45, charge[0] * 0.55),
                min(1.45, charge[1] * 0.55),
                min(1.45, charge[2] * 0.55),
                float(look['splatColor'][3]),
            )
            look['rimColor'] = (
                min(1.5, charge[0] * 0.7),
                min(1.5, charge[1] * 0.7),
                min(1.5, charge[2] * 0.7),
                float(look['rimColor'][3]),
            )
            look['smearColor'] = (
                min(1.35, charge[0] * 0.42),
                min(1.35, charge[1] * 0.42),
                min(1.35, charge[2] * 0.42),
                float(look['smearColor'][3]),
            )
    return look


class OverlordMagentaInkSplash(object):
    """Owns a brief magenta/crimson ink splash at a world position (hit or death)."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, pos, kind='hit', finaleLook=None, phase=1, parent=None):
        """Spawn splash at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = overlordMagentaInkSplashLook(
            kind, finaleLook=finaleLook, phase=phase)
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
            name='overlordMagentaInkSplash-%s' % look.get('id', kind),
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
        """Boss-scale billboard ink blob — smack / pop readability core."""
        try:
            half = float(look.get('splatHalf', 0.36))
            cm = CardMaker('overlord-magenta-ink-splash-core')
            cm.setFrame(-half, half, -half * 0.92, half * 0.92)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look['splatColor']
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0)
            splat.setScale(0.35)
            splat.setBin('fixed', int(look.get('binSort', 46)))
            splat.setDepthWrite(False)
            self._nodes.append(splat)

            # Hot rim so the smack reads against Silly magenta fog.
            rimHalf = half * float(look.get('rimScale', 1.32))
            cmRim = CardMaker('overlord-magenta-ink-splash-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.9)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin)
            rim.setBillboardPointEye()
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look['rimColor']
            rim.setColor(rimColor[0], rimColor[1], rimColor[2], 0.55)
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.3)
            rim.setBin('fixed', int(look.get('binSort', 46)) - 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('splatPeak', 1.85))
            sec = float(look.get('splatSec', 0.22))
            peakA = float(look.get('peakAlpha', 0.96))
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
        """Radial magenta smear — Overlord crown / rain streak cousin."""
        try:
            side = -1.0 if (index % 2) == 0 else 1.0
            t = 0.42 + 0.22 * (index // 2)
            angle = (pi * 0.38) + side * (0.3 + 0.18 * index)
            spread = float(look.get('smearSpread', 1.05))
            end = Point3(
                origin[0] + cos(angle) * spread * t,
                origin[1] + sin(angle) * spread * 0.5,
                origin[2] + 0.08 + sin(pi * 0.22 * index) * 0.28,
            )
            half = float(look.get('smearHalf', 0.12))
            cm = CardMaker('overlord-magenta-ink-splash-smear-%s' % index)
            cm.setFrame(-half, half, -half * 1.1, half * 1.1)
            smear = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + side * 0.06,
                origin[1] + 0.04,
                origin[2] + 0.05 * ((index % 3) - 1),
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
            smear.setBin('fixed', int(look.get('binSort', 46)) + 1)
            smear.setDepthWrite(False)
            self._nodes.append(smear)
            travel = float(look.get('smearSec', 0.24))
            delay = 0.012 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(smear, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(
                            smear, travel * 0.4, Point3(1.25, 0.7, 1.35),
                            blendType='easeOut'),
                        LerpScaleInterval(
                            smear, travel * 0.6, Point3(0.35, 0.25, 1.6),
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
            dist = float(look.get('fleckDist', 1.55)) * (0.65 + 0.16 * (index % 4))
            lift = float(look.get('fleckLift', 0.65)) * (0.5 + 0.18 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.15))
            if index % 2 == 0:
                cm = CardMaker('overlord-magenta-ink-splash-fleck-%s' % index)
                cm.setFrame(-half, half, -half, half)
                startScale = Point3(0.4, 0.4, 0.4)
                midScale = Point3(1.15, 1.15, 0.5)
                endScale = Point3(1.55, 1.55, 0.12)
            else:
                cm = CardMaker('overlord-magenta-ink-splash-streak-%s' % index)
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
            fleck.setBin('fixed', int(look.get('binSort', 46)) + 2)
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.28))
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
        """Soft falling drip — IdleInkDripFx / Overlord rain cousin."""
        try:
            angle = 0.9 + index * 1.1
            spread = float(look.get('dripSpread', 0.36)) * (0.45 + 0.15 * index)
            fall = float(look.get('dripFall', 1.05)) * (0.85 + 0.1 * index)
            end = Point3(
                origin[0] + sin(angle) * spread,
                origin[1] + cos(angle) * spread * 0.4,
                origin[2] - fall,
            )
            half = float(look.get('dripHalf', 0.1))
            if index % 2 == 0:
                cm = CardMaker('overlord-magenta-ink-splash-drip-%s' % index)
                cm.setFrame(-half, half, -half * 1.15, half * 1.15)
                startScale = Point3(0.4, 0.4, 0.5)
                midScale = Point3(0.6, 0.6, 1.05)
                endScale = Point3(0.95, 0.95, 0.18)
                color = look['dripColor']
            else:
                cm = CardMaker('overlord-magenta-ink-splash-drip-streak-%s' % index)
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
            drip.setBin('fixed', int(look.get('binSort', 46)) - 2)
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look.get('dripSec', 0.42))
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

"""Rubber-hose ink splat / pop juice when a CorruptToon is defeated.

World-space scale-burst companion + brief CardMaker droplet spray, layered
with CorruptDeathCreamFleckFx (sunny cream / pastel flecks — purity chips,
not ink), CorruptDeathCreamSparkleFx (rising cream / pastel sparkle flecks
from the fleck burst — telegraph / silhouette cream sparkle grammar), and
CorruptDeathCreamWashFx (soft cream wash pulse after the fleck burst —
reclaim purity-wash grammar). Wired from
DistributedCorruptToon.announceDefeat so Ink Smudge / Sludge Brute /
Balloon Snare deaths read as a Toontown gag splat — never KH / keyblade
framing.
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
from toontown.corruption.CorruptDeathCreamFleckFx import DeathCreamFleckBurst
from toontown.corruption.CorruptDeathCreamSparkleFx import DeathCreamSparkles
from toontown.corruption.CorruptDeathCreamWashFx import DeathCreamWashPulse


def deathPopLook(archetype):
    """Resolve splat palette / scale for an archetype (falls back to Ink)."""
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = CorruptionGlobals.ARCHETYPE_INK
    looks = CorruptionGlobals.DEATH_POP_LOOK
    return looks.get(aid, looks[CorruptionGlobals.ARCHETYPE_INK])


def buildBodyPopInterval(target, look=None, name='corruptDeathBodyPop'):
    """Scale burst → flat pancake → shrink-away Sequence (does not start).

    Caller owns start/finish. `target` is usually visualRoot (or self).
    """
    if target is None:
        return None
    look = look or deathPopLook(CorruptionGlobals.ARCHETYPE_INK)
    burst = Point3(*look['burstScale'])
    pancake = Point3(*look['pancakeScale'])
    vanish = Point3(*look['vanishScale'])
    burstColor = Vec4(*look['burstColor'])
    pancakeColor = Vec4(*look['pancakeColor'])
    fadeColor = Vec4(*look['fadeColor'])
    return Sequence(
        Parallel(
            LerpScaleInterval(
                target, float(look['burstSec']), burst, blendType='easeOut'),
            LerpColorScaleInterval(
                target, float(look['burstSec']), burstColor),
        ),
        Parallel(
            LerpScaleInterval(
                target, float(look['pancakeSec']), pancake,
                blendType='easeIn'),
            LerpColorScaleInterval(
                target, float(look['pancakeSec']), pancakeColor),
        ),
        Parallel(
            LerpScaleInterval(
                target, float(look['vanishSec']), vanish,
                blendType='easeIn'),
            LerpColorScaleInterval(
                target, float(look['vanishSec']), fadeColor),
        ),
        name=name,
    )


class DeathPopSplat(object):
    """Owns the brief ink-droplet / pop-spark spray at a world position."""

    def __init__(self):
        self._ival = None
        self._droplets = []
        self._ringNP = None
        self._sfx = None
        self._creamFlecks = None
        self._creamSparkles = None
        self._creamWash = None

    def play(self, pos, archetype=None, parent=None):
        """Spawn splat at `pos` (render space). Returns started Sequence or None."""
        self.clear()
        look = deathPopLook(archetype)
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
        ring = self._spawnRing(parentNP, origin, look)
        if ring is not None:
            parts.append(ring)

        count = int(look['dropletCount'])
        for i in range(count):
            part = self._spawnDroplet(parentNP, origin, look, i, count)
            if part is not None:
                parts.append(part)

        self._playSfx(look, origin, parentNP)

        # Sunny cream / pastel fleck layer — purity chips on the ink splat.
        try:
            cream = DeathCreamFleckBurst()
            cream.play(pos, archetype=archetype, parent=parentNP)
            self._creamFlecks = cream
        except Exception:
            self._creamFlecks = None

        # Rising cream sparkles from the fleck burst — telegraph/silhouette grammar.
        sparkleHold = 0.0
        try:
            from toontown.corruption.CorruptDeathCreamSparkleFx import (
                deathCreamSparkleLook)
            sparkles = DeathCreamSparkles()
            if sparkles.play(pos, archetype=archetype, parent=parentNP) is not None:
                self._creamSparkles = sparkles
                sparkleLook = deathCreamSparkleLook(archetype)
                fleckCount = max(0, int(sparkleLook.get('fleckCount', 0)))
                sparkleHold = (
                    float(sparkleLook.get('startDelaySec', 0.08))
                    + float(sparkleLook.get('fleckSec', 0.39))
                    + float(sparkleLook.get('fleckStagger', 0.038)) * max(
                        0, fleckCount - 1)
                    + 0.02)
            else:
                self._creamSparkles = None
        except Exception:
            self._creamSparkles = None

        # Soft cream wash pulse after fleck burst — reclaim purity-wash grammar.
        washHold = 0.0
        try:
            wash = DeathCreamWashPulse()
            if wash.play() is not None:
                self._creamWash = wash
                # Hold splat teardown beside delayed wash so clear() doesn't
                # kill the veil mid-pulse (wash self-clears too).
                washHold = (
                    float(getattr(
                        CorruptionGlobals, 'DEATH_CREAM_WASH_DELAY_SEC',
                        0.20))
                    + float(getattr(
                        CorruptionGlobals, 'DEATH_CREAM_WASH_IN_SEC', 0.06))
                    + float(getattr(
                        CorruptionGlobals, 'DEATH_CREAM_WASH_PULSE_SEC', 0.10))
                    + float(getattr(
                        CorruptionGlobals, 'DEATH_CREAM_WASH_HOLD_SEC', 0.08))
                    + float(getattr(
                        CorruptionGlobals, 'DEATH_CREAM_WASH_OUT_SEC', 0.42))
                    + 0.02)
            else:
                self._creamWash = None
        except Exception:
            self._creamWash = None

        layerHold = max(washHold, sparkleHold)
        if not parts and layerHold <= 0.0:
            return None

        hold = list(parts)
        if layerHold > 0.0:
            hold.append(Wait(layerHold))
        if not hold:
            return None

        self._ival = Sequence(
            Parallel(*hold),
            Func(self.clear),
            name='corruptDeathPopSplat',
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
        cream = self._creamFlecks
        self._creamFlecks = None
        if cream is not None:
            try:
                cream.clear()
            except Exception:
                pass
        sparkles = self._creamSparkles
        self._creamSparkles = None
        if sparkles is not None:
            try:
                sparkles.clear()
            except Exception:
                pass
        wash = self._creamWash
        self._creamWash = None
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        if self._ringNP is not None:
            try:
                if not self._ringNP.isEmpty():
                    self._ringNP.removeNode()
            except Exception:
                pass
            self._ringNP = None
        for np in self._droplets:
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._droplets = []

    def _spawnRing(self, parentNP, origin, look):
        try:
            half = float(look['ringHalf'])
            cm = CardMaker('corrupt-death-pop-ring')
            cm.setFrame(-half, half, -half, half)
            ring = parentNP.attachNewNode(cm.generate())
            ring.setPos(origin)
            ring.setBillboardPointEye()
            ring.setTransparency(TransparencyAttrib.MAlpha)
            color = look['ringColor']
            ring.setColor(color[0], color[1], color[2], color[3])
            ring.setColorScale(1, 1, 1, 0.85)
            ring.setScale(0.35)
            ring.setBin('fixed', 42)
            ring.setDepthWrite(False)
            self._ringNP = ring
            peak = float(look['ringPeak'])
            sec = float(look['ringSec'])
            return Sequence(
                Parallel(
                    LerpScaleInterval(ring, sec, peak, blendType='easeOut'),
                    LerpColorScaleInterval(
                        ring, sec, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            self._ringNP = None
            return None

    def _spawnDroplet(self, parentNP, origin, look, index, count):
        try:
            # Slight irregularity so the spray reads as ink, not a perfect star.
            angle = (2.0 * pi * index) / max(1, count) + (0.18 * (index % 3))
            dist = float(look['dropletDist']) * (0.7 + 0.18 * (index % 4))
            lift = float(look['dropletLift']) * (0.55 + 0.2 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look['dropletHalf'])
            # Alternate fat blobs vs thin streaks for rubber-hose splat variety.
            if index % 2 == 0:
                cm = CardMaker('corrupt-death-droplet-%s' % index)
                cm.setFrame(-half, half, -half, half)
                startScale = Point3(0.45, 0.45, 0.45)
                midScale = Point3(1.35, 1.35, 0.55)
                endScale = Point3(1.9, 1.9, 0.15)
            else:
                cm = CardMaker('corrupt-death-streak-%s' % index)
                cm.setFrame(-half * 0.45, half * 0.45, -half * 1.6, half * 1.6)
                startScale = Point3(0.35, 0.35, 0.7)
                midScale = Point3(0.7, 0.7, 1.55)
                endScale = Point3(1.4, 0.25, 0.2)
            drop = parentNP.attachNewNode(cm.generate())
            drop.setPos(origin)
            drop.setBillboardPointEye()
            drop.setTransparency(TransparencyAttrib.MAlpha)
            color = look['dropletColor']
            # Mild per-droplet tint variance so the spray isn't flat.
            tint = 0.85 + 0.12 * ((index * 3) % 5) / 4.0
            drop.setColor(
                min(1.5, color[0] * tint),
                min(1.5, color[1] * tint),
                min(1.5, color[2] * tint),
                color[3])
            drop.setScale(startScale)
            drop.setBin('fixed', 43)
            drop.setDepthWrite(False)
            self._droplets.append(drop)
            travel = float(look['dropletSec'])
            delay = 0.015 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(drop, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(drop, travel * 0.45, midScale),
                        LerpScaleInterval(drop, travel * 0.55, endScale),
                    ),
                    LerpColorScaleInterval(
                        drop, travel, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _playSfx(self, look, origin, parentNP):
        path = look.get('sfx')
        if not path:
            return
        try:
            if self._sfx is None:
                self._sfx = base.loader.loadSfx(path)  # noqa: F821
            sfx = self._sfx
            if not sfx:
                return
            volume = float(look.get(
                'sfxVolume', CorruptionGlobals.DEATH_POP_SFX_VOLUME))
            sfx.setVolume(volume)
            try:
                base.playSfx(sfx, node=parentNP)  # noqa: F821
            except Exception:
                base.playSfx(sfx)  # noqa: F821
        except Exception:
            self._sfx = False

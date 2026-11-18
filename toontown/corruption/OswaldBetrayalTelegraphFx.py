"""Short rubber-hose crimson stain-lunge telegraph for Corrupted Oswald.

World-space CardMaker juice wired from DistributedCorruptToon.announceAttackTelegraph
when archetype is ARCHETYPE_CORRUPT_OSWALD — a readable betrayal lunge / stain
charge so twist wind-ups scan apart from Ink Smudge purple fist, Brute spit,
Snare string, and Gagster puddle. Distinct from shared CorruptTelegraphInkFx
drip (already archetype-tinted). No cream deepen. Toontown spiritual sequel
only — no keyblades / no KH branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec3, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpHprInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def oswaldTelegraphStainLook():
    """Resolve betrayal-crimson stain-lunge telegraph palette / motion."""
    return dict(CorruptionGlobals.OSWALD_TELEGRAPH_STAIN_LOOK)


class OswaldBetrayalTelegraphStain(object):
    """Owns the brief crimson stain-lunge telegraph pop at a world position."""

    def __init__(self):
        self._ival = None
        self._root = None
        self._nodes = []

    def play(self, pos, parent=None):
        """Spawn stain-lunge pop at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = oswaldTelegraphStainLook()
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

        root = self._buildStainLunge(parentNP, origin, look)
        if root is None:
            return None
        self._root = root

        parts = [self._buildMainLungeInterval(root, look)]
        for part in self._buildCrimsonSmears(parentNP, origin, look):
            if part is not None:
                parts.append(part)

        parts = [p for p in parts if p is not None]
        if not parts:
            self.clear()
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='oswaldBetrayalTelegraphStain',
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
        root = self._root
        self._root = None
        if root is not None:
            try:
                if not root.isEmpty():
                    root.removeNode()
            except Exception:
                pass
        for np in self._nodes:
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _buildStainLunge(self, parentNP, origin, look):
        """Crimson stain blob + rim — betrayal lunge wind-up silhouette."""
        try:
            root = parentNP.attachNewNode('oswald-betrayal-telegraph-stain')
            root.setPos(origin)
            root.setBillboardPointEye()
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', int(look.get('binSort', 43)))
            root.setDepthWrite(False)
            root.setScale(float(look.get('scale', 1.05)))

            body = look.get('fistColor', (0.88, 0.16, 0.24, 1.0))
            rim = look.get('rimColor', (1.35, 0.42, 0.48, 1.0))
            half = float(look.get('fistHalf', 0.34))
            binSort = int(look.get('binSort', 43))

            # Main stain blob — rubber-hose lunge charge (not purple fist).
            cm = CardMaker('oswald-telegraph-stain-body')
            cm.setFrame(-half * 0.85, half * 1.15, -half * 0.95, half * 1.1)
            stain = root.attachNewNode(cm.generate())
            stain.setTransparency(TransparencyAttrib.MAlpha)
            stain.setColor(body[0], body[1], body[2], 1)
            stain.setBin('fixed', binSort)
            stain.setDepthWrite(False)

            # Hot crimson rim so the lunge pops against Silly / hub fog.
            cmRim = CardMaker('oswald-telegraph-stain-rim')
            rimHalf = half * float(look.get('rimScale', 1.36))
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.95)
            rimNP = root.attachNewNode(cmRim.generate())
            rimNP.setTransparency(TransparencyAttrib.MAlpha)
            rimNP.setColor(rim[0], rim[1], rim[2], 0.55)
            rimNP.setBin('fixed', binSort - 1)
            rimNP.setDepthWrite(False)
            rimNP.setPos(0.04, 0, -0.02)

            # Hot highlight — wet betrayal knuckle / stain tip.
            cmHot = CardMaker('oswald-telegraph-stain-hot')
            hotHalf = float(look.get('hotHalf', 0.12))
            cmHot.setFrame(-hotHalf, hotHalf, -hotHalf * 0.85, hotHalf * 0.85)
            hot = root.attachNewNode(cmHot.generate())
            hot.setTransparency(TransparencyAttrib.MAlpha)
            hot.setColor(rim[0], rim[1], rim[2], 1)
            hot.setBin('fixed', binSort + 1)
            hot.setDepthWrite(False)
            hot.setPos(half * 0.35, 0, half * 0.22)

            return root
        except Exception:
            return None

    def _buildMainLungeInterval(self, root, look):
        """Squash → forward lunge stretch → settle + crimson alpha flash."""
        try:
            if root is None or root.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(look.get('peakAlpha', 0.97))
        fadeIn = float(look.get('fadeInSec', 0.04))
        holdSec = float(look.get('holdSec', 0.14))
        fadeOut = float(look.get('fadeOutSec', 0.2))
        squash = look.get('squash', (1.95, 0.95, 0.32))
        stretch = look.get('stretch', (0.58, 1.05, 2.05))
        squashSec = float(look.get('squashSec', 0.045))
        stretchSec = float(look.get('stretchSec', 0.12))
        settleSec = float(look.get('settleSec', 0.12))
        baseScale = float(look.get('scale', 1.05))
        flash = look.get('flashColor', (1.55, 0.38, 0.45, 1.0))
        wobbleDeg = float(look.get('wobbleDeg', 18.0))

        squashScale = Vec3(
            baseScale * squash[0], baseScale * squash[1],
            baseScale * squash[2])
        stretchScale = Vec3(
            baseScale * stretch[0], baseScale * stretch[1],
            baseScale * stretch[2])
        settleScale = Vec3(baseScale, baseScale, baseScale)

        flashPeak = Vec4(
            min(1.7, flash[0] * 1.1),
            min(1.5, flash[1] * 1.1),
            min(1.5, flash[2] * 1.1),
            peakA,
        )

        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    root, fadeIn, flashPeak, blendType='easeOut'),
                Wait(holdSec),
                LerpColorScaleInterval(
                    root, fadeOut, Vec4(1, 1, 1, 0), blendType='easeIn'),
            ),
            Sequence(
                LerpScaleInterval(root, squashSec, squashScale),
                LerpScaleInterval(
                    root, stretchSec, stretchScale, blendType='easeOut'),
                LerpScaleInterval(
                    root, settleSec, settleScale, blendType='easeInOut'),
            ),
            # Sharper roll wobble — charged betrayal lunge, not Smudge fist.
            Sequence(
                LerpHprInterval(
                    root, squashSec + stretchSec * 0.5,
                    Point3(0, 0, wobbleDeg),
                    startHpr=Point3(0, 0, -wobbleDeg * 0.6),
                    blendType='easeOut'),
                LerpHprInterval(
                    root, settleSec + fadeOut * 0.35,
                    Point3(0, 0, 0), blendType='easeInOut'),
            ),
            name='oswaldTelegraphHoseLunge',
        )

    def _buildCrimsonSmears(self, parentNP, origin, look):
        """Tiny crimson stain smears fanning forward — betrayal lunge juice."""
        parts = []
        count = int(look.get('smearCount', 5))
        color = look.get('smearColor', (0.95, 0.22, 0.32, 0.92))
        half = float(look.get('smearHalf', 0.1))
        travel = float(look.get('smearSec', 0.26))
        spread = float(look.get('smearSpread', 1.05))
        for i in range(count):
            try:
                # Forward-biased smear burst — lunge, not radial punch fist.
                side = -1.0 if (i % 2) == 0 else 1.0
                t = 0.4 + 0.22 * (i // 2)
                angle = (pi * 0.15) + side * (0.28 + 0.16 * i)
                end = Point3(
                    origin[0] + cos(angle) * spread * t * 1.15,
                    origin[1] + sin(angle) * spread * 0.45,
                    origin[2] + 0.06 + sin(pi * 0.22 * i) * 0.24,
                )
                cm = CardMaker('oswald-telegraph-smear-%s' % i)
                cm.setFrame(-half, half, -half * 1.2, half * 1.2)
                smear = parentNP.attachNewNode(cm.generate())
                start = Point3(
                    origin[0] + side * 0.05,
                    origin[1] + 0.06,
                    origin[2] + 0.04 * ((i % 3) - 1),
                )
                smear.setPos(start)
                smear.setBillboardPointEye()
                smear.setTransparency(TransparencyAttrib.MAlpha)
                tint = 0.9 + 0.08 * (i % 3)
                smear.setColor(
                    min(1.45, color[0] * tint),
                    min(1.35, color[1] * tint),
                    min(1.35, color[2] * tint),
                    color[3])
                smear.setScale(Point3(0.5, 0.55, 0.75))
                smear.setBin('fixed', int(look.get('binSort', 43)) + 2)
                smear.setDepthWrite(False)
                self._nodes.append(smear)
                delay = 0.014 * i
                midScale = Point3(1.3, 0.7, 1.4)
                endScale = Point3(0.35, 0.28, 1.85)
                parts.append(Sequence(
                    Wait(delay),
                    Parallel(
                        LerpPosInterval(
                            smear, travel, end, blendType='easeOut'),
                        Sequence(
                            LerpScaleInterval(
                                smear, travel * 0.4, midScale,
                                blendType='easeOut'),
                            LerpScaleInterval(
                                smear, travel * 0.6, endScale,
                                blendType='easeIn'),
                        ),
                        LerpColorScaleInterval(
                            smear, travel, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ))
            except Exception:
                continue
        return parts

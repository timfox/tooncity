"""Short rubber-hose purple ink telegraph pop for Ink Smudge.

World-space CardMaker juice wired from DistributedCorruptToon.announceAttackTelegraph
when archetype is Ink Smudge — a readable melee ink-fist / smear charge so close-
range wind-ups scan apart from Brute spit-gob and Balloon Snare string-lash.
Distinct from the shared CorruptTelegraphInkFx drip. Toontown spiritual sequel
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


def smudgeTelegraphInkLook():
    """Resolve purple ink-fist telegraph palette / motion."""
    return dict(CorruptionGlobals.SMUDGE_TELEGRAPH_INK_LOOK)


class SmudgeInkTelegraphFist(object):
    """Owns the brief purple ink-fist telegraph pop at a world position."""

    def __init__(self):
        self._ival = None
        self._root = None
        self._nodes = []

    def play(self, pos, parent=None):
        """Spawn ink-fist pop at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = smudgeTelegraphInkLook()
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

        root = self._buildInkFist(parentNP, origin, look)
        if root is None:
            return None
        self._root = root

        parts = [self._buildMainFistInterval(root, look)]
        for part in self._buildInkSmears(parentNP, origin, look):
            if part is not None:
                parts.append(part)

        parts = [p for p in parts if p is not None]
        if not parts:
            self.clear()
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='smudgeInkTelegraphFist',
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

    def _buildInkFist(self, parentNP, origin, look):
        """Rounded purple ink fist + rim — melee telegraph wind-up silhouette."""
        try:
            root = parentNP.attachNewNode('smudge-ink-telegraph-fist')
            root.setPos(origin)
            root.setBillboardPointEye()
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', int(look.get('binSort', 42)))
            root.setDepthWrite(False)
            root.setScale(float(look.get('scale', 1.0)))

            body = look.get('fistColor', (0.55, 0.18, 0.95, 1.0))
            rim = look.get('rimColor', (1.15, 0.45, 1.55, 1.0))
            half = float(look.get('fistHalf', 0.36))
            binSort = int(look.get('binSort', 42))

            # Main ink fist — rubber-hose melee charge blob (not spit, not string).
            cm = CardMaker('smudge-telegraph-ink-body')
            cm.setFrame(-half, half, -half * 0.9, half * 1.05)
            fist = root.attachNewNode(cm.generate())
            fist.setTransparency(TransparencyAttrib.MAlpha)
            fist.setColor(body[0], body[1], body[2], 1)
            fist.setBin('fixed', binSort)
            fist.setDepthWrite(False)

            # Bright purple rim so the fist pops against Loopy ink drip.
            cmRim = CardMaker('smudge-telegraph-ink-rim')
            rimHalf = half * float(look.get('rimScale', 1.32))
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.88, rimHalf * 0.95)
            rimNP = root.attachNewNode(cmRim.generate())
            rimNP.setTransparency(TransparencyAttrib.MAlpha)
            rimNP.setColor(rim[0], rim[1], rim[2], 0.52)
            rimNP.setBin('fixed', binSort - 1)
            rimNP.setDepthWrite(False)
            rimNP.setPos(0, 0, -0.02)

            # Hot highlight — wet ink knuckle read.
            cmHot = CardMaker('smudge-telegraph-ink-hot')
            hotHalf = float(look.get('hotHalf', 0.13))
            cmHot.setFrame(-hotHalf, hotHalf, -hotHalf * 0.85, hotHalf * 0.85)
            hot = root.attachNewNode(cmHot.generate())
            hot.setTransparency(TransparencyAttrib.MAlpha)
            hot.setColor(rim[0], rim[1], rim[2], 1)
            hot.setBin('fixed', binSort + 1)
            hot.setDepthWrite(False)
            hot.setPos(half * 0.2, 0, half * 0.26)

            return root
        except Exception:
            return None

    def _buildMainFistInterval(self, root, look):
        """Squash → punch stretch → settle + purple alpha flash."""
        try:
            if root is None or root.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(look.get('peakAlpha', 0.96))
        fadeIn = float(look.get('fadeInSec', 0.04))
        holdSec = float(look.get('holdSec', 0.15))
        fadeOut = float(look.get('fadeOutSec', 0.22))
        # Melee punch charge: wide flat squash → forward punch stretch.
        squash = look.get('squash', (1.75, 1.0, 0.38))
        stretch = look.get('stretch', (0.7, 1.0, 1.85))
        squashSec = float(look.get('squashSec', 0.05))
        stretchSec = float(look.get('stretchSec', 0.11))
        settleSec = float(look.get('settleSec', 0.13))
        baseScale = float(look.get('scale', 1.0))
        flash = look.get('flashColor', (1.35, 0.45, 1.7, 1.0))
        wobbleDeg = float(look.get('wobbleDeg', 14.0))

        squashScale = Vec3(
            baseScale * squash[0], baseScale * squash[1],
            baseScale * squash[2])
        stretchScale = Vec3(
            baseScale * stretch[0], baseScale * stretch[1],
            baseScale * stretch[2])
        settleScale = Vec3(baseScale, baseScale, baseScale)

        flashPeak = Vec4(
            min(1.6, flash[0] * 1.1),
            min(1.6, flash[1] * 1.1),
            min(1.6, flash[2] * 1.1),
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
            # Tiny roll wobble so the fist feels charged, not static.
            Sequence(
                LerpHprInterval(
                    root, squashSec + stretchSec * 0.5,
                    Point3(0, 0, wobbleDeg),
                    startHpr=Point3(0, 0, -wobbleDeg * 0.5),
                    blendType='easeOut'),
                LerpHprInterval(
                    root, settleSec + fadeOut * 0.35,
                    Point3(0, 0, 0), blendType='easeInOut'),
            ),
            name='smudgeTelegraphHoseFist',
        )

    def _buildInkSmears(self, parentNP, origin, look):
        """Tiny purple ink smears fanning outward — rubber-hose melee juice."""
        parts = []
        count = int(look.get('smearCount', 4))
        color = look.get('smearColor', (0.75, 0.28, 1.15, 0.9))
        half = float(look.get('smearHalf', 0.11))
        travel = float(look.get('smearSec', 0.28))
        spread = float(look.get('smearSpread', 0.95))
        for i in range(count):
            try:
                # Radial smear burst — melee wind-up, not spit arc or lash.
                side = -1.0 if (i % 2) == 0 else 1.0
                t = 0.35 + 0.25 * (i // 2)
                angle = (pi * 0.45) + side * (0.35 + 0.2 * i)
                end = Point3(
                    origin[0] + cos(angle) * spread * t,
                    origin[1] + sin(angle) * spread * 0.55,
                    origin[2] + 0.08 + sin(pi * 0.25 * i) * 0.28,
                )
                cm = CardMaker('smudge-telegraph-smear-%s' % i)
                cm.setFrame(-half, half, -half * 1.15, half * 1.15)
                smear = parentNP.attachNewNode(cm.generate())
                start = Point3(
                    origin[0] + side * 0.06,
                    origin[1] + 0.05,
                    origin[2] + 0.05 * ((i % 3) - 1),
                )
                smear.setPos(start)
                smear.setBillboardPointEye()
                smear.setTransparency(TransparencyAttrib.MAlpha)
                tint = 0.88 + 0.1 * (i % 3)
                smear.setColor(
                    min(1.4, color[0] * tint),
                    min(1.4, color[1] * tint),
                    min(1.4, color[2] * tint),
                    color[3])
                smear.setScale(Point3(0.55, 0.55, 0.7))
                smear.setBin('fixed', int(look.get('binSort', 42)) + 2)
                smear.setDepthWrite(False)
                self._nodes.append(smear)
                delay = 0.016 * i
                midScale = Point3(1.25, 0.75, 1.35)
                endScale = Point3(0.4, 0.3, 1.7)
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

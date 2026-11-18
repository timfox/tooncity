"""Short rubber-hose green spit telegraph pop for Sludge Brute.

World-space CardMaker juice wired from DistributedCorruptToon.announceAttackTelegraph
when archetype is Sludge Brute — a readable forward spit-gob charge so ranged
wind-ups scan apart from Smudge ink drip and Balloon Snare string-lash. Distinct
from the hit-time spit blob (__playSpitBlob). Toontown spiritual sequel only —
no keyblades / no KH branding.
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


def bruteTelegraphSpitLook():
    """Resolve green spit-gob telegraph palette / motion."""
    return dict(CorruptionGlobals.BRUTE_TELEGRAPH_SPIT_LOOK)


class BruteSpitTelegraphGob(object):
    """Owns the brief green spit-gob telegraph pop at a world position."""

    def __init__(self):
        self._ival = None
        self._root = None
        self._nodes = []

    def play(self, pos, parent=None):
        """Spawn spit-gob pop at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = bruteTelegraphSpitLook()
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

        root = self._buildSpitGob(parentNP, origin, look)
        if root is None:
            return None
        self._root = root

        parts = [self._buildMainGobInterval(root, look)]
        for part in self._buildSpitDroplets(parentNP, origin, look):
            if part is not None:
                parts.append(part)

        parts = [p for p in parts if p is not None]
        if not parts:
            self.clear()
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='bruteSpitTelegraphGob',
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

    def _buildSpitGob(self, parentNP, origin, look):
        """Rounded green spit gob + bright rim — telegraph wind-up silhouette."""
        try:
            root = parentNP.attachNewNode('brute-spit-telegraph-gob')
            root.setPos(origin)
            root.setBillboardPointEye()
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', int(look.get('binSort', 44)))
            root.setDepthWrite(False)
            root.setScale(float(look.get('scale', 1.0)))

            body = look.get('gobColor', (0.22, 0.85, 0.28, 1.0))
            rim = look.get('rimColor', (0.55, 1.2, 0.42, 1.0))
            half = float(look.get('gobHalf', 0.38))
            binSort = int(look.get('binSort', 44))

            # Main spit gob — reads as a charged rubber-hose spit bubble.
            cm = CardMaker('brute-telegraph-spit-body')
            cm.setFrame(-half, half, -half * 0.95, half * 1.05)
            gob = root.attachNewNode(cm.generate())
            gob.setTransparency(TransparencyAttrib.MAlpha)
            gob.setColor(body[0], body[1], body[2], 1)
            gob.setBin('fixed', binSort)
            gob.setDepthWrite(False)

            # Bright rim ring so the gob pops against sludge drip green.
            cmRim = CardMaker('brute-telegraph-spit-rim')
            rimHalf = half * float(look.get('rimScale', 1.28))
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.95)
            rimNP = root.attachNewNode(cmRim.generate())
            rimNP.setTransparency(TransparencyAttrib.MAlpha)
            rimNP.setColor(rim[0], rim[1], rim[2], 0.55)
            rimNP.setBin('fixed', binSort - 1)
            rimNP.setDepthWrite(False)
            rimNP.setPos(0, 0, -0.02)

            # Hot highlight bulb — rubber-hose wet spit read.
            cmHot = CardMaker('brute-telegraph-spit-hot')
            hotHalf = float(look.get('hotHalf', 0.14))
            cmHot.setFrame(-hotHalf, hotHalf, -hotHalf * 0.85, hotHalf * 0.85)
            hot = root.attachNewNode(cmHot.generate())
            hot.setTransparency(TransparencyAttrib.MAlpha)
            hot.setColor(rim[0], rim[1], rim[2], 1)
            hot.setBin('fixed', binSort + 1)
            hot.setDepthWrite(False)
            hot.setPos(half * 0.22, 0, half * 0.28)

            return root
        except Exception:
            return None

    def _buildMainGobInterval(self, root, look):
        """Squash → tall rubber spit stretch → settle + green alpha flash."""
        try:
            if root is None or root.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(look.get('peakAlpha', 0.97))
        fadeIn = float(look.get('fadeInSec', 0.04))
        holdSec = float(look.get('holdSec', 0.16))
        fadeOut = float(look.get('fadeOutSec', 0.24))
        # Tall spit charge: wide flat → thin tall (opposite Snare horizontal lash).
        squash = look.get('squash', (1.65, 1.0, 0.42))
        stretch = look.get('stretch', (0.55, 1.0, 2.15))
        squashSec = float(look.get('squashSec', 0.05))
        stretchSec = float(look.get('stretchSec', 0.12))
        settleSec = float(look.get('settleSec', 0.14))
        baseScale = float(look.get('scale', 1.0))
        flash = look.get('flashColor', (0.55, 1.35, 0.4, 1.0))
        wobbleDeg = float(look.get('wobbleDeg', 12.0))

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
            # Tiny roll wobble so the gob feels charged, not static.
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
            name='bruteTelegraphHoseSpit',
        )

    def _buildSpitDroplets(self, parentNP, origin, look):
        """Tiny green spit droplets spraying forward — rubber-hose juice."""
        parts = []
        count = int(look.get('dropletCount', 4))
        color = look.get('dropletColor', (0.35, 0.95, 0.3, 0.9))
        half = float(look.get('dropletHalf', 0.1))
        travel = float(look.get('dropletSec', 0.3))
        spread = float(look.get('dropletSpread', 1.05))
        for i in range(count):
            try:
                # Fan forward/outward in a shallow spit arc (not downward drip).
                side = -1.0 if (i % 2) == 0 else 1.0
                t = 0.4 + 0.22 * (i // 2)
                angle = side * (0.2 + 0.18 * i)
                end = Point3(
                    origin[0] + side * spread * t * 0.55,
                    origin[1] + cos(angle) * spread * 0.85,
                    origin[2] + 0.15 + sin(pi * 0.2 * i) * 0.35,
                )
                cm = CardMaker('brute-telegraph-droplet-%s' % i)
                cm.setFrame(-half, half, -half * 0.9, half * 1.1)
                drop = parentNP.attachNewNode(cm.generate())
                start = Point3(
                    origin[0] + side * 0.08,
                    origin[1] + 0.1,
                    origin[2] + 0.06 * ((i % 3) - 1),
                )
                drop.setPos(start)
                drop.setBillboardPointEye()
                drop.setTransparency(TransparencyAttrib.MAlpha)
                tint = 0.88 + 0.1 * (i % 3)
                drop.setColor(
                    min(1.4, color[0] * tint),
                    min(1.4, color[1] * tint),
                    min(1.4, color[2] * tint),
                    color[3])
                drop.setScale(Point3(0.5, 0.5, 0.65))
                drop.setBin('fixed', int(look.get('binSort', 44)) + 2)
                drop.setDepthWrite(False)
                self._nodes.append(drop)
                delay = 0.018 * i
                midScale = Point3(1.35, 0.7, 1.45)
                endScale = Point3(0.35, 0.25, 1.9)
                parts.append(Sequence(
                    Wait(delay),
                    Parallel(
                        LerpPosInterval(
                            drop, travel, end, blendType='easeOut'),
                        Sequence(
                            LerpScaleInterval(
                                drop, travel * 0.4, midScale,
                                blendType='easeOut'),
                            LerpScaleInterval(
                                drop, travel * 0.6, endScale,
                                blendType='easeIn'),
                        ),
                        LerpColorScaleInterval(
                            drop, travel, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ))
            except Exception:
                continue
        return parts

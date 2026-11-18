"""Short rubber-hose amber string-lash telegraph pop for Balloon Snare.

World-space CardMaker juice wired from DistributedCorruptToon.announceAttackTelegraph
when archetype is Balloon Snare — a readable horizontal string whip so zip/lash
wind-ups scan apart from Smudge ink drip and Brute spit. Distinct from the
hit-time string snap (__playStringLash). Toontown spiritual sequel only —
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


def snareTelegraphStringLook():
    """Resolve amber string-lash telegraph palette / motion."""
    return dict(CorruptionGlobals.SNARE_TELEGRAPH_STRING_LOOK)


class BalloonSnareTelegraphString(object):
    """Owns the brief amber string-lash telegraph pop at a world position."""

    def __init__(self):
        self._ival = None
        self._root = None
        self._nodes = []

    def play(self, pos, parent=None):
        """Spawn string-lash pop at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = snareTelegraphStringLook()
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

        root = self._buildLashBundle(parentNP, origin, look)
        if root is None:
            return None
        self._root = root

        parts = [self._buildMainLashInterval(root, look)]
        for part in self._buildWhipStreaks(parentNP, origin, look):
            if part is not None:
                parts.append(part)

        parts = [p for p in parts if p is not None]
        if not parts:
            self.clear()
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='balloonSnareTelegraphString',
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

    def _buildLashBundle(self, parentNP, origin, look):
        """Horizontal rubber-hose string + knot tip — telegraph wind-up silhouette."""
        try:
            root = parentNP.attachNewNode('balloon-snare-telegraph-string')
            root.setPos(origin)
            root.setBillboardPointEye()
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', int(look.get('binSort', 43)))
            root.setDepthWrite(False)
            root.setScale(float(look.get('scale', 1.0)))

            body = look.get('stringColor', (0.95, 0.55, 0.12, 1.0))
            tip = look.get('tipColor', (1.15, 0.75, 0.28, 1.0))
            halfW = float(look.get('stringHalfW', 0.55))
            halfH = float(look.get('stringHalfH', 0.08))
            binSort = int(look.get('binSort', 43))

            # Main horizontal string — reads as a rubber lash charging sideways.
            cm = CardMaker('snare-telegraph-string-body')
            cm.setFrame(-halfW, halfW, -halfH, halfH)
            strand = root.attachNewNode(cm.generate())
            strand.setTransparency(TransparencyAttrib.MAlpha)
            strand.setColor(body[0], body[1], body[2], 1)
            strand.setBin('fixed', binSort)
            strand.setDepthWrite(False)

            # Soft mid knot so the lash doesn't read as a flat bar.
            cmKnot = CardMaker('snare-telegraph-string-knot')
            knotR = float(look.get('knotHalf', 0.11))
            cmKnot.setFrame(-knotR, knotR, -knotR * 0.85, knotR * 0.85)
            knot = root.attachNewNode(cmKnot.generate())
            knot.setTransparency(TransparencyAttrib.MAlpha)
            knot.setColor(tip[0], tip[1], tip[2], 1)
            knot.setBin('fixed', binSort + 1)
            knot.setDepthWrite(False)

            # Tip bulbs on both ends — balloon-string read.
            tipHalf = float(look.get('tipHalf', 0.1))
            for name, cx in (('tip-l', -halfW * 0.92), ('tip-r', halfW * 0.92)):
                cmTip = CardMaker('snare-telegraph-%s' % name)
                cmTip.setFrame(
                    cx - tipHalf, cx + tipHalf, -tipHalf * 0.9, tipHalf * 0.9)
                tipNP = root.attachNewNode(cmTip.generate())
                tipNP.setTransparency(TransparencyAttrib.MAlpha)
                tipNP.setColor(tip[0], tip[1], tip[2], 1)
                tipNP.setBin('fixed', binSort + 1)
                tipNP.setDepthWrite(False)

            return root
        except Exception:
            return None

    def _buildMainLashInterval(self, root, look):
        """Squash → horizontal rubber stretch → settle + amber alpha flash."""
        try:
            if root is None or root.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(look.get('peakAlpha', 0.96))
        fadeIn = float(look.get('fadeInSec', 0.04))
        holdSec = float(look.get('holdSec', 0.14))
        fadeOut = float(look.get('fadeOutSec', 0.22))
        # Horizontal rubber-hose lash: thin tall → wide flat.
        squash = look.get('squash', (0.45, 1.0, 1.55))
        stretch = look.get('stretch', (2.35, 1.0, 0.42))
        squashSec = float(look.get('squashSec', 0.05))
        stretchSec = float(look.get('stretchSec', 0.1))
        settleSec = float(look.get('settleSec', 0.12))
        baseScale = float(look.get('scale', 1.0))
        flash = look.get('flashColor', (1.25, 0.8, 0.35, 1.0))
        whipDeg = float(look.get('whipDeg', 18.0))

        squashScale = Vec3(
            baseScale * squash[0], baseScale * squash[1],
            baseScale * squash[2])
        stretchScale = Vec3(
            baseScale * stretch[0], baseScale * stretch[1],
            baseScale * stretch[2])
        settleScale = Vec3(baseScale, baseScale, baseScale)

        flashPeak = Vec4(
            min(1.6, flash[0] * 1.12),
            min(1.6, flash[1] * 1.12),
            min(1.6, flash[2] * 1.12),
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
            # Tiny roll whip so the string feels lashed, not static.
            Sequence(
                LerpHprInterval(
                    root, squashSec + stretchSec * 0.5,
                    Point3(0, 0, whipDeg), startHpr=Point3(0, 0, -whipDeg * 0.6),
                    blendType='easeOut'),
                LerpHprInterval(
                    root, settleSec + fadeOut * 0.35,
                    Point3(0, 0, 0), blendType='easeInOut'),
            ),
            name='snareTelegraphHoseLash',
        )

    def _buildWhipStreaks(self, parentNP, origin, look):
        """Tiny amber whip streaks fanning sideways — rubber-hose juice."""
        parts = []
        count = int(look.get('streakCount', 3))
        color = look.get('streakColor', (1.05, 0.65, 0.22, 0.9))
        half = float(look.get('streakHalf', 0.12))
        travel = float(look.get('streakSec', 0.28))
        spread = float(look.get('streakSpread', 1.15))
        for i in range(count):
            try:
                # Fan left/right in a shallow arc (horizontal lash, not drip).
                side = -1.0 if (i % 2) == 0 else 1.0
                t = 0.35 + 0.28 * (i // 2)
                angle = side * (0.15 + 0.22 * i)
                end = Point3(
                    origin[0] + side * spread * t,
                    origin[1] + cos(angle) * spread * 0.2,
                    origin[2] + sin(pi * 0.15 * i) * 0.18,
                )
                cm = CardMaker('snare-telegraph-streak-%s' % i)
                cm.setFrame(-half * 1.8, half * 1.8, -half * 0.35, half * 0.35)
                streak = parentNP.attachNewNode(cm.generate())
                start = Point3(
                    origin[0] + side * 0.12,
                    origin[1],
                    origin[2] + 0.04 * ((i % 3) - 1),
                )
                streak.setPos(start)
                streak.setBillboardPointEye()
                streak.setTransparency(TransparencyAttrib.MAlpha)
                tint = 0.9 + 0.08 * (i % 3)
                streak.setColor(
                    min(1.4, color[0] * tint),
                    min(1.4, color[1] * tint),
                    min(1.4, color[2] * tint),
                    color[3])
                streak.setScale(Point3(0.45, 0.45, 0.7))
                streak.setBin('fixed', int(look.get('binSort', 43)) + 2)
                streak.setDepthWrite(False)
                self._nodes.append(streak)
                delay = 0.015 * i
                midScale = Point3(1.55, 0.55, 0.55)
                endScale = Point3(2.1, 0.2, 0.15)
                parts.append(Sequence(
                    Wait(delay),
                    Parallel(
                        LerpPosInterval(
                            streak, travel, end, blendType='easeOut'),
                        Sequence(
                            LerpScaleInterval(
                                streak, travel * 0.45, midScale,
                                blendType='easeOut'),
                            LerpScaleInterval(
                                streak, travel * 0.55, endScale,
                                blendType='easeIn'),
                        ),
                        LerpColorScaleInterval(
                            streak, travel, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ))
            except Exception:
                continue
        return parts

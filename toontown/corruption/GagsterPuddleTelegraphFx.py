"""Short rubber-hose teal gag-lob puddle telegraph warn for Gunk Gagster.

World-space CardMaker juice wired from DistributedCorruptToon.announceAttackTelegraph
when archetype is Gunk Gagster — a readable bounce-pie charge on the Gagster plus
a cream/ink ground puddle warn at the lob landing so Punchline players can dodge
out during wind-up. Distinct from hit-time __playGagLob / __playGagPuddle and from
Brute spit / Snare lash / Smudge fist telegraphs. Toontown spiritual sequel only —
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


def gagsterTelegraphPuddleLook():
    """Resolve teal gag-lob puddle telegraph palette / motion."""
    return dict(CorruptionGlobals.GAGSTER_TELEGRAPH_PUDDLE_LOOK)


class GagsterPuddleTelegraphWarn(object):
    """Owns bounce-pie charge + cream/ink puddle warn at telegraph start."""

    def __init__(self):
        self._ival = None
        self._root = None
        self._nodes = []

    def play(self, pos, warnPos=None, parent=None):
        """Spawn pie charge at `pos` + puddle warn at `warnPos`.

        `pos` is Gagster render space. `warnPos` is the predicted puddle
        landing (usually local avatar feet); falls back to `pos` XY.
        Returns Sequence or None.
        """
        self.clear()
        look = gagsterTelegraphPuddleLook()
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

        if warnPos is None:
            warnOrigin = Point3(origin[0], origin[1], float(look.get(
                'puddleLift', 0.1)))
            try:
                warnOrigin = Point3(
                    pos[0], pos[1],
                    float(pos[2]) + float(look.get('puddleLift', 0.1)))
            except Exception:
                pass
        else:
            try:
                warnOrigin = Point3(
                    warnPos[0], warnPos[1],
                    float(warnPos[2]) + float(look.get('puddleLift', 0.1)))
            except Exception:
                warnOrigin = Point3(
                    origin[0], origin[1], float(look.get('puddleLift', 0.1)))

        root = self._buildBouncePie(parentNP, origin, look)
        if root is None:
            return None
        self._root = root

        parts = [self._buildMainPieInterval(root, look)]
        puddle = self._buildPuddleWarn(parentNP, warnOrigin, look)
        if puddle is not None:
            parts.append(puddle)
        for part in self._buildCreamWarnFlecks(parentNP, warnOrigin, look):
            if part is not None:
                parts.append(part)
        for part in self._buildInkDroplets(parentNP, origin, look):
            if part is not None:
                parts.append(part)

        parts = [p for p in parts if p is not None]
        if not parts:
            self.clear()
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='gagsterPuddleTelegraphWarn',
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

    def _buildBouncePie(self, parentNP, origin, look):
        """Teal bounce-bomb pie + cream rim — gag-lob wind-up silhouette."""
        try:
            root = parentNP.attachNewNode('gagster-puddle-telegraph-pie')
            root.setPos(origin)
            root.setBillboardPointEye()
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', int(look.get('binSort', 44)))
            root.setDepthWrite(False)
            root.setScale(float(look.get('scale', 1.0)))

            body = look.get('pieColor', (0.18, 0.82, 0.88, 1.0))
            rim = look.get('creamRimColor', (1.15, 1.05, 0.82, 1.0))
            half = float(look.get('pieHalf', 0.36))
            binSort = int(look.get('binSort', 44))

            # Main teal pie — reads as a charged rubber-hose gag bounce-bomb.
            cm = CardMaker('gagster-telegraph-pie-body')
            cm.setFrame(-half, half, -half * 0.95, half * 1.05)
            pie = root.attachNewNode(cm.generate())
            pie.setTransparency(TransparencyAttrib.MAlpha)
            pie.setColor(body[0], body[1], body[2], 1)
            pie.setBin('fixed', binSort)
            pie.setDepthWrite(False)

            # Cream rim ring — sunny warn contrast against teal ink/gunk.
            cmRim = CardMaker('gagster-telegraph-pie-cream-rim')
            rimHalf = half * float(look.get('rimScale', 1.3))
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.95)
            rimNP = root.attachNewNode(cmRim.generate())
            rimNP.setTransparency(TransparencyAttrib.MAlpha)
            rimNP.setColor(rim[0], rim[1], rim[2], 0.58)
            rimNP.setBin('fixed', binSort - 1)
            rimNP.setDepthWrite(False)
            rimNP.setPos(0, 0, -0.02)

            # Hot cream highlight bulb — rubber-hose wet gag read.
            cmHot = CardMaker('gagster-telegraph-pie-hot')
            hotHalf = float(look.get('hotHalf', 0.13))
            cmHot.setFrame(-hotHalf, hotHalf, -hotHalf * 0.85, hotHalf * 0.85)
            hot = root.attachNewNode(cmHot.generate())
            hot.setTransparency(TransparencyAttrib.MAlpha)
            hot.setColor(rim[0], rim[1], rim[2], 1)
            hot.setBin('fixed', binSort + 1)
            hot.setDepthWrite(False)
            hot.setPos(half * 0.2, 0, half * 0.3)

            return root
        except Exception:
            return None

    def _buildMainPieInterval(self, root, look):
        """Crouch squash → upward toss stretch → settle + teal/cream flash."""
        try:
            if root is None or root.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(look.get('peakAlpha', 0.97))
        fadeIn = float(look.get('fadeInSec', 0.04))
        holdSec = float(look.get('holdSec', 0.18))
        fadeOut = float(look.get('fadeOutSec', 0.26))
        # Lob charge: wide crouch → tall toss (matches Gagster body telegraph).
        squash = look.get('squash', (1.55, 1.0, 0.48))
        stretch = look.get('stretch', (0.62, 1.0, 2.05))
        squashSec = float(look.get('squashSec', 0.05))
        stretchSec = float(look.get('stretchSec', 0.12))
        settleSec = float(look.get('settleSec', 0.14))
        baseScale = float(look.get('scale', 1.0))
        flash = look.get('flashColor', (0.45, 1.35, 1.45, 1.0))
        bounceDeg = float(look.get('bounceDeg', 14.0))

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
            # Tiny roll bounce so the pie feels charged for a lob toss.
            Sequence(
                LerpHprInterval(
                    root, squashSec + stretchSec * 0.5,
                    Point3(0, 0, bounceDeg),
                    startHpr=Point3(0, 0, -bounceDeg * 0.5),
                    blendType='easeOut'),
                LerpHprInterval(
                    root, settleSec + fadeOut * 0.35,
                    Point3(0, 0, 0), blendType='easeInOut'),
            ),
            name='gagsterTelegraphHosePie',
        )

    def _buildPuddleWarn(self, parentNP, warnOrigin, look):
        """Flat cream-rimmed teal puddle ring — landing trap warn on the ground."""
        try:
            half = float(look.get('puddleHalf', 1.05))
            binSort = int(look.get('binSort', 44)) - 2

            # Soft cream under-ring so the warn reads sunny vs teal ink.
            cream = look.get('puddleCreamColor', (1.12, 1.02, 0.78, 0.72))
            cmCream = CardMaker('gagster-telegraph-puddle-cream')
            creamHalf = half * float(look.get('puddleCreamScale', 1.22))
            cmCream.setFrame(-creamHalf, creamHalf, -creamHalf, creamHalf)
            creamNP = parentNP.attachNewNode(cmCream.generate())
            creamNP.setPos(warnOrigin)
            creamNP.setP(-90)
            creamNP.setTransparency(TransparencyAttrib.MAlpha)
            creamNP.setColor(cream[0], cream[1], cream[2], cream[3])
            creamNP.setColorScale(1, 1, 1, 0)
            creamNP.setScale(0.28)
            creamNP.setBin('fixed', binSort)
            creamNP.setDepthWrite(False)
            self._nodes.append(creamNP)

            # Teal ink puddle core — trap radius silhouette.
            ink = look.get('puddleInkColor', (0.12, 0.62, 0.72, 0.82))
            cmInk = CardMaker('gagster-telegraph-puddle-ink')
            cmInk.setFrame(-half, half, -half, half)
            inkNP = parentNP.attachNewNode(cmInk.generate())
            inkNP.setPos(warnOrigin[0], warnOrigin[1], warnOrigin[2] + 0.02)
            inkNP.setP(-90)
            inkNP.setTransparency(TransparencyAttrib.MAlpha)
            inkNP.setColor(ink[0], ink[1], ink[2], ink[3])
            inkNP.setColorScale(1, 1, 1, 0)
            inkNP.setScale(0.32)
            inkNP.setBin('fixed', binSort + 1)
            inkNP.setDepthWrite(False)
            self._nodes.append(inkNP)

            peak = float(look.get('puddlePeak', 2.2))
            fadeIn = float(look.get('puddleInSec', 0.14))
            hold = float(look.get('puddleHoldSec', 0.28))
            fadeOut = float(look.get('puddleOutSec', 0.32))
            delay = float(look.get('puddleDelay', 0.06))
            peakA = float(look.get('peakAlpha', 0.97)) * 0.78
            creamPeak = peak * float(look.get('puddleCreamPeakScale', 1.12))

            return Sequence(
                Wait(delay),
                Parallel(
                    Sequence(
                        Parallel(
                            LerpScaleInterval(
                                creamNP, fadeIn, creamPeak, blendType='easeOut'),
                            LerpColorScaleInterval(
                                creamNP, fadeIn, Vec4(1, 1, 1, peakA * 0.85),
                                blendType='easeOut'),
                        ),
                        Wait(hold),
                        Parallel(
                            LerpScaleInterval(
                                creamNP, fadeOut, creamPeak * 1.18,
                                blendType='easeIn'),
                            LerpColorScaleInterval(
                                creamNP, fadeOut, Vec4(1, 1, 1, 0),
                                blendType='easeIn'),
                        ),
                    ),
                    Sequence(
                        Parallel(
                            LerpScaleInterval(
                                inkNP, fadeIn, peak, blendType='easeOut'),
                            LerpColorScaleInterval(
                                inkNP, fadeIn, Vec4(1, 1, 1, peakA),
                                blendType='easeOut'),
                        ),
                        Wait(hold),
                        Parallel(
                            LerpScaleInterval(
                                inkNP, fadeOut, peak * 1.15, blendType='easeIn'),
                            LerpColorScaleInterval(
                                inkNP, fadeOut, Vec4(1, 1, 1, 0),
                                blendType='easeIn'),
                        ),
                    ),
                ),
                name='gagsterTelegraphPuddleWarn',
            )
        except Exception:
            return None

    def _buildCreamWarnFlecks(self, parentNP, warnOrigin, look):
        """Sunny cream flecks around the puddle warn — rubber-hose cream contrast."""
        parts = []
        count = int(look.get('creamFleckCount', 5))
        color = look.get('creamFleckColor', (1.15, 1.05, 0.8, 0.92))
        half = float(look.get('creamFleckHalf', 0.1))
        travel = float(look.get('creamFleckSec', 0.34))
        spread = float(look.get('creamFleckSpread', 1.05))
        lift = float(look.get('creamFleckLift', 0.55))
        for i in range(count):
            try:
                angle = (2.0 * pi * i) / max(1, count) + 0.18
                t = 0.45 + 0.18 * (i % 3)
                end = Point3(
                    warnOrigin[0] + cos(angle) * spread * t,
                    warnOrigin[1] + sin(angle) * spread * t,
                    warnOrigin[2] + lift * (0.55 + 0.2 * (i % 3)),
                )
                cm = CardMaker('gagster-telegraph-cream-fleck-%s' % i)
                cm.setFrame(-half, half, -half * 0.85, half * 1.05)
                fleck = parentNP.attachNewNode(cm.generate())
                start = Point3(
                    warnOrigin[0] + cos(angle) * 0.12,
                    warnOrigin[1] + sin(angle) * 0.12,
                    warnOrigin[2] + 0.08,
                )
                fleck.setPos(start)
                fleck.setBillboardPointEye()
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                tint = 0.9 + 0.08 * (i % 3)
                fleck.setColor(
                    min(1.4, color[0] * tint),
                    min(1.4, color[1] * tint),
                    min(1.4, color[2] * tint),
                    color[3])
                fleck.setScale(Point3(0.45, 0.45, 0.65))
                fleck.setBin('fixed', int(look.get('binSort', 44)) + 2)
                fleck.setDepthWrite(False)
                self._nodes.append(fleck)
                delay = 0.02 * i + float(look.get('puddleDelay', 0.06))
                midScale = Point3(1.25, 0.75, 1.35)
                endScale = Point3(0.35, 0.25, 1.6)
                parts.append(Sequence(
                    Wait(delay),
                    Parallel(
                        LerpPosInterval(
                            fleck, travel, end, blendType='easeOut'),
                        Sequence(
                            LerpScaleInterval(
                                fleck, travel * 0.4, midScale,
                                blendType='easeOut'),
                            LerpScaleInterval(
                                fleck, travel * 0.6, endScale,
                                blendType='easeIn'),
                        ),
                        LerpColorScaleInterval(
                            fleck, travel, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ))
            except Exception:
                continue
        return parts

    def _buildInkDroplets(self, parentNP, origin, look):
        """Tiny teal ink droplets spraying upward — lob charge juice."""
        parts = []
        count = int(look.get('dropletCount', 4))
        color = look.get('dropletColor', (0.22, 0.85, 0.9, 0.9))
        half = float(look.get('dropletHalf', 0.09))
        travel = float(look.get('dropletSec', 0.3))
        spread = float(look.get('dropletSpread', 0.85))
        for i in range(count):
            try:
                side = -1.0 if (i % 2) == 0 else 1.0
                t = 0.35 + 0.2 * (i // 2)
                angle = side * (0.18 + 0.16 * i)
                end = Point3(
                    origin[0] + side * spread * t * 0.45,
                    origin[1] + cos(angle) * spread * 0.35,
                    origin[2] + 0.35 + sin(pi * 0.22 * i) * 0.55,
                )
                cm = CardMaker('gagster-telegraph-droplet-%s' % i)
                cm.setFrame(-half, half, -half * 0.9, half * 1.1)
                drop = parentNP.attachNewNode(cm.generate())
                start = Point3(
                    origin[0] + side * 0.06,
                    origin[1],
                    origin[2] + 0.05 * ((i % 3) - 1),
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
                delay = 0.016 * i
                midScale = Point3(1.3, 0.7, 1.4)
                endScale = Point3(0.3, 0.22, 1.85)
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

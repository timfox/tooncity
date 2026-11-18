"""Rubber-hose ground-slam dust / ink puff at feet.

Client juice when the combo-finisher stretch-punch slam connects: a short
horizontal dust ring + warm dust / ink flecks pop at foot level so the thud
reads on the street. Toontown spiritual-sequel tone only — no keyblades /
no KH branding.
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
)

from . import HackSlashConfig


class SlamDustFx(object):
    """Owns one short world-space dust/ink burst at foot level."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._nodes = []

    def play(self, origin=None, parent=None):
        """Spawn dust/ink pop at feet. Returns started Sequence or None.

        `origin` is render-space; defaults to the local avatar's feet.
        """
        if not getattr(HackSlashConfig, 'FINISHER_SLAM_DUST_ENABLED', True):
            return None
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        if origin is None:
            try:
                pos = self.avatar.getPos(parentNP)
            except Exception:
                return None
        else:
            try:
                pos = Point3(origin[0], origin[1], origin[2])
            except Exception:
                return None

        lift = float(HackSlashConfig.FINISHER_SLAM_DUST_LIFT)
        feet = Point3(pos[0], pos[1], pos[2] + lift)
        parts = []

        ring = self._spawnRing(parentNP, feet)
        if ring is not None:
            parts.append(ring)

        for i in range(int(HackSlashConfig.FINISHER_SLAM_DUST_PUFF_COUNT)):
            part = self._spawnPuff(parentNP, feet, i, ink=False)
            if part is not None:
                parts.append(part)

        for i in range(int(HackSlashConfig.FINISHER_SLAM_DUST_INK_COUNT)):
            part = self._spawnPuff(parentNP, feet, i, ink=True)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashSlamDust'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the burst and remove every dust/ink node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        for np in list(self._nodes):
            self._retireNode(np)
        self._nodes = []

    def _spawnRing(self, parentNP, feet):
        """Flat ground-plane ring that expands + fades (reads as slam thud)."""
        half = float(HackSlashConfig.FINISHER_SLAM_DUST_RING_HALF)
        peak = float(HackSlashConfig.FINISHER_SLAM_DUST_RING_PEAK)
        sec = float(HackSlashConfig.FINISHER_SLAM_DUST_RING_SEC)
        r, g, b, a = HackSlashConfig.FINISHER_SLAM_DUST_RING_COLOR
        er, eg, eb, ea = HackSlashConfig.FINISHER_SLAM_DUST_RING_END_COLOR
        try:
            cm = CardMaker('hackslash-slam-dust-ring')
            cm.setFrame(-half, half, -half, half)
            ring = parentNP.attachNewNode(cm.generate())
            # Lay flat on the street — not an eye billboard.
            ring.setP(-90)
            ring.setPos(feet)
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, a)
            ring.setScale(0.35)
            ring.setBin('transparent', 20)
            ring.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(ring)
        return Parallel(
            LerpScaleInterval(ring, sec, peak, blendType='easeOut'),
            LerpColorScaleInterval(
                ring, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        )

    def _spawnPuff(self, parentNP, feet, index, ink=False):
        """Outward dust blob or ink fleck with a short rubber-hose squash pop."""
        if ink:
            count = max(1, int(HackSlashConfig.FINISHER_SLAM_DUST_INK_COUNT))
            size = float(HackSlashConfig.FINISHER_SLAM_DUST_INK_SIZE)
            drift = float(HackSlashConfig.FINISHER_SLAM_DUST_INK_DRIFT)
            lift = float(HackSlashConfig.FINISHER_SLAM_DUST_INK_LIFT)
            sec = float(HackSlashConfig.FINISHER_SLAM_DUST_INK_SEC)
            r, g, b, a = HackSlashConfig.FINISHER_SLAM_DUST_INK_COLOR
            er, eg, eb, ea = HackSlashConfig.FINISHER_SLAM_DUST_INK_END_COLOR
            angleBias = 0.85
            name = 'hackslash-slam-ink-%s' % index
        else:
            count = max(1, int(HackSlashConfig.FINISHER_SLAM_DUST_PUFF_COUNT))
            size = float(HackSlashConfig.FINISHER_SLAM_DUST_PUFF_SIZE)
            drift = float(HackSlashConfig.FINISHER_SLAM_DUST_PUFF_DRIFT)
            lift = float(HackSlashConfig.FINISHER_SLAM_DUST_PUFF_LIFT)
            sec = float(HackSlashConfig.FINISHER_SLAM_DUST_PUFF_SEC)
            r, g, b, a = HackSlashConfig.FINISHER_SLAM_DUST_PUFF_COLOR
            er, eg, eb, ea = HackSlashConfig.FINISHER_SLAM_DUST_PUFF_END_COLOR
            angleBias = 0.22
            name = 'hackslash-slam-dust-%s' % index

        angle = (2.0 * pi * index) / float(count) + angleBias * (1 + (index % 3))
        try:
            cm = CardMaker(name)
            # Alternate fat blobs vs thin streaks for rubber-hose variety.
            if index % 2 == 0:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            else:
                cm.setFrame(-size * 0.55, size * 0.55, -size * 1.35, size * 1.35)
            puff = parentNP.attachNewNode(cm.generate())
            puff.setTransparency(TransparencyAttrib.MAlpha)
            puff.setColor(r, g, b, 1)
            puff.setColorScale(r, g, b, a)
            start = Point3(
                feet[0] + cos(angle) * 0.2,
                feet[1] + sin(angle) * 0.2,
                feet[2] + 0.04 * (index % 2))
            puff.setPos(start)
            # Start slightly flat so the pop reads as a ground kick-up.
            puff.setScale(0.55 + 0.12 * (index % 3), 0.55, 0.35)
            puff.setBin('transparent', 21)
            puff.setDepthWrite(False)
            puff.setBillboardPointEye()
        except Exception:
            return None

        end = Point3(
            feet[0] + cos(angle) * drift,
            feet[1] + sin(angle) * drift,
            feet[2] + lift + 0.12 * (index % 3))
        midScale = Point3(
            1.15 + 0.1 * (index % 2),
            1.15 + 0.1 * (index % 2),
            0.75 + 0.15 * (index % 2))
        self._nodes.append(puff)
        return Sequence(
            Parallel(
                LerpPosInterval(puff, sec * 0.55, end, blendType='easeOut'),
                LerpScaleInterval(
                    puff, sec * 0.4, midScale, blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(puff, sec * 0.45, 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    puff, sec * 0.45, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def _retireNode(self, np):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass

"""Rubber-hose ink sparkle / star pop for a perfect dodge.

Client juice when Shift/X dodge i-frames eat a CorruptToon telegraph hit
(or a near-miss while those i-frames are live). Warm cream stars + ink
flecks — Toontown spiritual-sequel tone only, no keyblades / no KH branding.
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


class DodgePerfectFx(object):
    """Owns a short world-space sparkle burst at the local toon."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._nodes = []

    def play(self, parent=None):
        """Spawn star/ink pop at the avatar. Returns started Sequence or None."""
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            pos = self.avatar.getPos(parentNP)
        except Exception:
            return None

        lift = float(HackSlashConfig.PERFECT_DODGE_LIFT)
        origin = Point3(pos[0], pos[1], pos[2] + lift)
        parts = []

        for i in range(int(HackSlashConfig.PERFECT_DODGE_STAR_COUNT)):
            part = self._spawnStar(parentNP, origin, i)
            if part is not None:
                parts.append(part)

        for i in range(int(HackSlashConfig.PERFECT_DODGE_FLECK_COUNT)):
            part = self._spawnFleck(parentNP, origin, i)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashPerfectDodge'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the burst and remove every star/fleck node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        for np in list(self._nodes):
            self._retireNode(np)
        self._nodes = []

    def _spawnStar(self, parentNP, origin, index):
        count = max(1, int(HackSlashConfig.PERFECT_DODGE_STAR_COUNT))
        size = float(HackSlashConfig.PERFECT_DODGE_STAR_SIZE)
        drift = float(HackSlashConfig.PERFECT_DODGE_STAR_DRIFT)
        sec = float(HackSlashConfig.PERFECT_DODGE_STAR_SEC)
        r, g, b, a = HackSlashConfig.PERFECT_DODGE_STAR_COLOR
        er, eg, eb, ea = HackSlashConfig.PERFECT_DODGE_STAR_END_COLOR
        # Irregular star arms so it reads as cartoon ink glitter, not a glyph.
        angle = (2.0 * pi * index) / float(count) + 0.22 * (index % 3)
        try:
            cm = CardMaker('hackslash-perfect-star-%s' % index)
            cm.setFrame(-size, size, -size * 0.35, size * 0.35)
            star = parentNP.attachNewNode(cm.generate())
            star.setTransparency(TransparencyAttrib.MAlpha)
            star.setColor(r, g, b, 1)
            star.setColorScale(r, g, b, a)
            star.setPos(
                origin[0] + cos(angle) * 0.18,
                origin[1] + sin(angle) * 0.18,
                origin[2] + 0.05 * (index % 2))
            star.setScale(0.35 + 0.1 * (index % 3))
            star.setH(angle * 57.2957795)
            star.setBin('transparent', 24)
            star.setDepthWrite(False)
            star.setBillboardPointEye()
        except Exception:
            return None

        end = Point3(
            origin[0] + cos(angle) * drift,
            origin[1] + sin(angle) * drift,
            origin[2] + 0.35 + 0.15 * (index % 2))
        peak = size * (1.55 + 0.12 * (index % 2))
        self._nodes.append(star)
        return Sequence(
            Parallel(
                LerpPosInterval(star, sec * 0.55, end, blendType='easeOut'),
                LerpScaleInterval(
                    star, sec * 0.35, peak, blendType='easeOut'),
                LerpColorScaleInterval(
                    star, sec * 0.55, Vec4(r, g, b, a), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(star, sec * 0.45, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    star, sec * 0.45, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def _spawnFleck(self, parentNP, origin, index):
        count = max(1, int(HackSlashConfig.PERFECT_DODGE_FLECK_COUNT))
        size = float(HackSlashConfig.PERFECT_DODGE_FLECK_SIZE)
        drift = float(HackSlashConfig.PERFECT_DODGE_FLECK_DRIFT)
        sec = float(HackSlashConfig.PERFECT_DODGE_FLECK_SEC)
        r, g, b, a = HackSlashConfig.PERFECT_DODGE_FLECK_COLOR
        er, eg, eb, ea = HackSlashConfig.PERFECT_DODGE_FLECK_END_COLOR
        angle = (2.0 * pi * index) / float(count) + 0.7
        try:
            cm = CardMaker('hackslash-perfect-fleck-%s' % index)
            cm.setFrame(-size, size, -size, size)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            fleck.setPos(
                origin[0] + cos(angle) * 0.12,
                origin[1] + sin(angle) * 0.12,
                origin[2] - 0.1)
            fleck.setScale(0.5 + 0.15 * (index % 3))
            fleck.setBin('transparent', 23)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return None

        end = Point3(
            origin[0] + cos(angle) * drift,
            origin[1] + sin(angle) * drift,
            origin[2] - 0.45 - 0.12 * (index % 3))
        self._nodes.append(fleck)
        return Parallel(
            LerpPosInterval(fleck, sec, end, blendType='easeOut'),
            LerpScaleInterval(fleck, sec, 0.05, blendType='easeIn'),
            LerpColorScaleInterval(
                fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        )

    def _retireNode(self, np):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass

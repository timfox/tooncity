"""Rubber-hose ink sparkle / star pop for a perfect dodge.

Client juice when Shift/X dodge i-frames eat a CorruptToon telegraph hit
(or a near-miss while those i-frames are live). Warm cream stars + ink
flecks, then a delayed cream star aftershock, then a soft cream wash
pulse + residual cream wash aftershock — Toontown spiritual-sequel tone
only, no keyblades / no KH branding.
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

from . import HackSlashConfig
from .PerfectDodgeCreamWashFx import PerfectDodgeCreamWashPulse


class DodgePerfectFx(object):
    """Owns sparkle burst + cream star aftershock + cream wash + wash aftershock."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._nodes = []
        self._haloNP = None
        self._creamWash = None

    def play(self, parent=None):
        """Spawn star/ink pop + cream aftershock + delayed cream wash aftershock.

        Returns started Sequence or None.
        """
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

        # Residual cream star aftershock after the initial pop settles.
        aftershock = self._buildAftershock(parentNP, origin)
        if aftershock is not None:
            burst = Parallel(
                Parallel(*parts),
                aftershock,
            )
        else:
            burst = Parallel(*parts)

        # Soft cream wash pulse + wash aftershock — entry/purity grammar.
        washHold = 0.0
        try:
            wash = PerfectDodgeCreamWashPulse()
            if wash.play() is not None:
                self._creamWash = wash
                # Hold teardown beside delayed wash + residual aftershock so
                # clear() doesn't kill the veil/flecks mid-pulse (wash
                # self-clears too).
                washDuration = (
                    float(getattr(
                        HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_IN_SEC',
                        0.06))
                    + float(getattr(
                        HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_PULSE_SEC',
                        0.10))
                    + float(getattr(
                        HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_HOLD_SEC',
                        0.08))
                    + float(getattr(
                        HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_OUT_SEC',
                        0.40)))
                aftershockTail = 0.0
                if getattr(
                        HackSlashConfig,
                        'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_ENABLED', True):
                    aftershockTail = (
                        float(getattr(
                            HackSlashConfig,
                            'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                            0.22))
                        + float(getattr(
                            HackSlashConfig,
                            'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_SEC',
                            0.32))
                        + 0.05)
                washHold = (
                    float(getattr(
                        HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_DELAY_SEC',
                        0.40))
                    + max(washDuration, aftershockTail)
                    + 0.04)
            else:
                self._creamWash = None
        except Exception:
            self._creamWash = None

        hold = [burst]
        if washHold > 0.0:
            hold.append(Wait(washHold))

        self._ival = Sequence(
            Parallel(*hold),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashPerfectDodge'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop burst/aftershock/wash and remove every star/fleck/halo/wash."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._creamWash
        self._creamWash = None
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        if self._haloNP is not None:
            self._retireNode(self._haloNP)
            self._haloNP = None
        for np in list(self._nodes):
            self._retireNode(np)
        self._nodes = []

    def _buildAftershock(self, parentNP, origin):
        """Delayed soft cream stars (+ optional halo) after the initial pop."""
        if not getattr(
                HackSlashConfig, 'PERFECT_DODGE_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_AFTERSHOCK_DELAY_SEC', 0.22))
        parts = []

        if getattr(
                HackSlashConfig,
                'PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_COUNT', 4))
        for i in range(count):
            part = self._spawnAftershockStar(parentNP, origin, i, count)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parentNP, origin):
        half = float(HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_HALF)
        startScale = float(
            HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_START)
        peakScale = float(
            HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_PEAK)
        sec = float(HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_SEC)
        peakA = float(
            HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA)
        r, g, b, _a = HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_COLOR
        try:
            cm = CardMaker('hackslash-perfect-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            halo.setBin('transparent', 22)
            halo.setDepthWrite(False)
            halo.setBillboardPointEye()
        except Exception:
            return None
        self._haloNP = halo
        return Parallel(
            LerpScaleInterval(
                halo, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.2)),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.8), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _spawnAftershockStar(self, parentNP, origin, index, total):
        """Softer cream star that settles downward — residual aftershock."""
        count = max(1, int(total))
        size = float(HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_SIZE)
        drift = float(HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_DRIFT)
        sec = float(HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_SEC)
        r, g, b, a = HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_COLOR
        er, eg, eb, ea = HackSlashConfig.PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_END
        angle = (2.0 * pi * index) / float(count) + 0.35
        try:
            cm = CardMaker('hackslash-perfect-cream-aftershock-star-%s' % index)
            cm.setFrame(-size, size, -size * 0.35, size * 0.35)
            star = parentNP.attachNewNode(cm.generate())
            star.setTransparency(TransparencyAttrib.MAlpha)
            star.setColor(r, g, b, 1)
            star.setColorScale(r, g, b, 0)
            star.setPos(
                origin[0] + cos(angle) * 0.12,
                origin[1] + sin(angle) * 0.12,
                origin[2] + 0.04 * (index % 2))
            star.setScale(0.28 + 0.08 * (index % 3))
            star.setH(angle * 57.2957795)
            star.setBin('transparent', 25)
            star.setDepthWrite(False)
            star.setBillboardPointEye()
        except Exception:
            return None

        # Settle downward — residual cream, not the initial outward glitter.
        end = Point3(
            origin[0] + cos(angle) * drift * 0.55,
            origin[1] + sin(angle) * drift * 0.55,
            origin[2] - 0.55 - 0.12 * (index % 3))
        peak = size * (1.25 + 0.1 * (index % 2))
        self._nodes.append(star)
        delay = 0.02 * (index % 3)
        return Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(
                    star, 0.06, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    star, sec * 0.3, peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(star, sec * 0.7, end, blendType='easeIn'),
                LerpScaleInterval(
                    star, sec * 0.7, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    star, sec * 0.7, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

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

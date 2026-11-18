"""Rubber-hose cream aftershock after the Oswald finale reveal sting.

Soft cream flash + expanding ring + sparse settling flecks that fire
*after* FinalePhaseFx's ink flash / shadow sting lands. Supports the
twist beat (residual victory cream colliding with the truth) without
undoing it — quieter and later than CampaignHandoffConfetti's victory
cream swell (#82), which clears before the reveal. Toontown spiritual
sequel — no keyblades / no KH branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

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

from toontown.campaign import CampaignGlobals


class FinaleCreamAftershockFx(object):
    """Owns one soft cream aftershock burst under aspect2d."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._flashNP = None
        self._ringNP = None

    def play(self, origin=None, parent=None):
        """Spawn cream aftershock. Returns started Sequence or None."""
        if not getattr(
                CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = aspect2d  # noqa: F821
            except Exception:
                return None

        if origin is None:
            origin = getattr(
                CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_ORIGIN',
                (0.0, 0.0, 0.08))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.08

        binSort = int(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_BIN', 58))
        parts = []

        flashPart = self._spawnFlash(parentNP, ox, oy, oz, binSort)
        if flashPart is not None:
            parts.append(flashPart)

        ringPart = self._spawnRing(parentNP, ox, oy, oz, binSort)
        if ringPart is not None:
            parts.append(ringPart)

        fleckCount = int(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_COUNT', 8))
        for i in range(fleckCount):
            part = self._spawnFleck(
                parentNP, ox, oy, oz, i, fleckCount, binSort)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='finaleRevealCreamAftershock',
        )
        self._ival.start()
        return self._ival

    def _spawnFlash(self, parentNP, ox, oy, oz, binSort):
        r, g, b, _a = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_COLOR',
            (1.0, 0.96, 0.82, 1.0))
        peak = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_PEAK', 0.18))
        inSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_IN_SEC', 0.08))
        holdSec = float(getattr(
            CampaignGlobals,
            'FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_HOLD_SEC', 0.06))
        outSec = float(getattr(
            CampaignGlobals,
            'FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_OUT_SEC', 0.55))
        try:
            cm = CardMaker('finale-cream-aftershock-flash')
            cm.setFrame(-2.0, 2.0, -2.0, 2.0)
            flash = parentNP.attachNewNode(cm.generate())
            flash.setTransparency(TransparencyAttrib.MAlpha)
            flash.setColor(r, g, b, 1)
            flash.setColorScale(r, g, b, 0)
            flash.setPos(ox, oy, oz)
            flash.setBin('fixed', binSort)
            flash.setDepthTest(False)
            flash.setDepthWrite(False)
            self._flashNP = flash
        except Exception:
            self._flashNP = None
            return None
        return Sequence(
            LerpColorScaleInterval(
                flash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                flash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
        )

    def _spawnRing(self, parentNP, ox, oy, oz, binSort):
        r, g, b, _a = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_RING_COLOR',
            (1.0, 0.94, 0.74, 1.0))
        peakScale = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_RING_PEAK', 1.85))
        sec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_RING_SEC', 0.62))
        peakA = float(getattr(
            CampaignGlobals,
            'FINALE_REVEAL_CREAM_AFTERSHOCK_RING_PEAK_ALPHA', 0.28))
        startScale = float(getattr(
            CampaignGlobals,
            'FINALE_REVEAL_CREAM_AFTERSHOCK_RING_START', 0.28))
        try:
            cm = CardMaker('finale-cream-aftershock-ring')
            cm.setFrame(-0.5, 0.5, -0.5, 0.5)
            ring = parentNP.attachNewNode(cm.generate())
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, peakA)
            ring.setScale(startScale)
            ring.setPos(ox, oy, oz)
            ring.setBin('fixed', binSort + 1)
            ring.setDepthTest(False)
            ring.setDepthWrite(False)
            self._ringNP = ring
        except Exception:
            self._ringNP = None
            return None
        return Parallel(
            LerpScaleInterval(
                ring, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.2)),
                LerpColorScaleInterval(
                    ring, max(0.01, sec * 0.8), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _spawnFleck(self, parentNP, ox, oy, oz, index, total, binSort):
        colors = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        size = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_SIZE', 0.022))
        drift = float(getattr(
            CampaignGlobals,
            'FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_DRIFT', 0.42))
        sec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_SEC', 0.85))
        # Settle *downward* — residual cream aftershock, not carnival lift.
        angle = (2.0 * pi * index) / float(max(1, total)) + 0.4
        wide = (index % 2) == 0
        try:
            cm = CardMaker('finale-cream-aftershock-fleck-%s' % index)
            if wide:
                cm.setFrame(
                    -size * 1.3, size * 1.3, -size * 0.5, size * 0.5)
            else:
                cm.setFrame(
                    -size * 0.5, size * 0.5, -size * 1.2, size * 1.2)
            bit = parentNP.attachNewNode(cm.generate())
            bit.setTransparency(TransparencyAttrib.MAlpha)
            bit.setColor(r, g, b, 1)
            bit.setColorScale(r, g, b, 0)
            start = Point3(
                ox + cos(angle) * 0.04,
                oy,
                oz + sin(angle) * 0.03)
            bit.setPos(start)
            bit.setScale(0.28)
            bit.setR(angle * 30.0)
            bit.setBin('fixed', binSort + 2)
            bit.setDepthTest(False)
            bit.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(bit)
        end = Point3(
            start[0] + cos(angle) * drift * 0.7,
            oy,
            start[2] - abs(sin(angle)) * drift * 0.55 - 0.18)
        delay = 0.025 * (index % 4)
        return Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(
                    bit, 0.08, Vec4(r, g, b, a), blendType='easeOut'),
                # Soft squash → settle (hose drip, not victory swell pop).
                LerpScaleInterval(
                    bit, 0.07, Point3(1.4, 1, 0.5), blendType='easeOut'),
            ),
            LerpScaleInterval(
                bit, 0.09, Point3(0.7, 1, 1.25), blendType='easeOut'),
            Parallel(
                LerpPosInterval(bit, sec, end, blendType='easeIn'),
                LerpScaleInterval(
                    bit, sec, Point3(0.1, 1, 0.1), blendType='easeIn'),
                LerpColorScaleInterval(
                    bit, sec, Vec4(r, g, b, 0), blendType='easeIn'),
                LerpHprInterval(
                    bit, sec,
                    Point3(0, 0, bit.getR() + 90 + 20 * (index % 3)),
                    blendType='easeOut'),
            ),
        )

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        for attr in ('_flashNP', '_ringNP'):
            np = getattr(self, attr, None)
            if np is not None:
                try:
                    if not np.isEmpty():
                        np.removeNode()
                except Exception:
                    pass
                setattr(self, attr, None)
        for np in list(self._nodes):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []


_aftershock = None


def ensureFinaleCreamAftershockFx():
    global _aftershock
    if _aftershock is None:
        _aftershock = FinaleCreamAftershockFx()
    return _aftershock


def playFinaleCreamAftershock(origin=None, parent=None):
    """Fire the reveal cream aftershock. Returns Sequence or None."""
    return ensureFinaleCreamAftershockFx().play(origin=origin, parent=parent)


def clearFinaleCreamAftershock():
    """Stop/clear any in-flight reveal cream aftershock."""
    if _aftershock is not None:
        _aftershock.clear()

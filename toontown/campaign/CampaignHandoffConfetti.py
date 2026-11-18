"""Rubber-hose confetti / streamer pop for campaign act handoffs.

Short aspect2d carnival burst when Loopy→Punchline (or act) celebration
fires from CampaignHandoff. Squash/stretch streamers + drifting confetti
bits — Toontown spiritual sequel, never keyblade / KH framing.
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


class HandoffConfettiPop(object):
    """Owns one brief confetti + streamer burst on aspect2d."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def play(self, origin=None, parent=None):
        """Spawn pop at `origin` (aspect2d). Returns started Sequence or None."""
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = aspect2d  # noqa: F821
            except Exception:
                return None

        if origin is None:
            origin = getattr(
                CampaignGlobals, 'HANDOFF_CONFETTI_ORIGIN', (0.0, 0.0, 0.38))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.38

        parts = []
        confettiCount = int(getattr(
            CampaignGlobals, 'HANDOFF_CONFETTI_COUNT', 10))
        for i in range(confettiCount):
            part = self._spawnConfetti(parentNP, ox, oy, oz, i, confettiCount)
            if part is not None:
                parts.append(part)

        streamerCount = int(getattr(
            CampaignGlobals, 'HANDOFF_STREAMER_COUNT', 5))
        for i in range(streamerCount):
            part = self._spawnStreamer(parentNP, ox, oy, oz, i, streamerCount)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='campaignHandoffConfettiPop',
        )
        self._ival.start()
        return self._ival

    def _spawnConfetti(self, parentNP, ox, oy, oz, index, total):
        colors = getattr(CampaignGlobals, 'HANDOFF_CONFETTI_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        size = float(getattr(CampaignGlobals, 'HANDOFF_CONFETTI_SIZE', 0.028))
        drift = float(getattr(CampaignGlobals, 'HANDOFF_CONFETTI_DRIFT', 0.55))
        sec = float(getattr(CampaignGlobals, 'HANDOFF_CONFETTI_SEC', 0.72))
        angle = (2.0 * pi * index) / float(max(1, total)) + 0.35
        # Alternate wide vs tall bits — rubber-hose confetti chips.
        wide = (index % 2) == 0
        try:
            cm = CardMaker('handoff-confetti-%s' % index)
            if wide:
                cm.setFrame(-size * 1.35, size * 1.35, -size * 0.55, size * 0.55)
            else:
                cm.setFrame(-size * 0.55, size * 0.55, -size * 1.25, size * 1.25)
            bit = parentNP.attachNewNode(cm.generate())
            bit.setTransparency(TransparencyAttrib.MAlpha)
            bit.setColor(r, g, b, 1)
            bit.setColorScale(r, g, b, 0)
            start = Point3(
                ox + cos(angle) * 0.04,
                oy,
                oz + sin(angle) * 0.03)
            bit.setPos(start)
            bit.setScale(0.35)
            bit.setR(angle * 40.0)
            bit.setBin('fixed', 64)
            bit.setDepthTest(False)
            bit.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(bit)
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + abs(sin(angle)) * drift * 0.85 - 0.12)
        delay = 0.018 * (index % 4)
        return Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(
                    bit, 0.08, Vec4(r, g, b, a), blendType='easeOut'),
                # Flat squash → stretch pop, then settle drift.
                LerpScaleInterval(
                    bit, 0.07, Point3(1.55, 1, 0.45), blendType='easeOut'),
            ),
            LerpScaleInterval(
                bit, 0.09, Point3(0.65, 1, 1.45), blendType='easeOut'),
            Parallel(
                LerpPosInterval(bit, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    bit, sec, Point3(0.15, 1, 0.15), blendType='easeIn'),
                LerpColorScaleInterval(
                    bit, sec, Vec4(r, g, b, 0), blendType='easeIn'),
                LerpHprInterval(
                    bit, sec, Point3(0, 0, bit.getR() + 180 + 40 * (index % 3)),
                    blendType='easeOut'),
            ),
        )

    def _spawnStreamer(self, parentNP, ox, oy, oz, index, total):
        colors = getattr(CampaignGlobals, 'HANDOFF_STREAMER_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        frame = getattr(
            CampaignGlobals, 'HANDOFF_STREAMER_FRAME',
            (-0.012, 0.012, -0.09, 0.09))
        drift = float(getattr(CampaignGlobals, 'HANDOFF_STREAMER_DRIFT', 0.72))
        sec = float(getattr(CampaignGlobals, 'HANDOFF_STREAMER_SEC', 0.85))
        # Fan streamers upward from the banner — rubber-hose ribbon lash.
        fan = -55.0 + (110.0 * index) / float(max(1, total - 1))
        angle = (fan * pi) / 180.0
        try:
            cm = CardMaker('handoff-streamer-%s' % index)
            cm.setFrame(*frame)
            ribbon = parentNP.attachNewNode(cm.generate())
            ribbon.setTransparency(TransparencyAttrib.MAlpha)
            ribbon.setColor(r, g, b, 1)
            ribbon.setColorScale(r, g, b, 0)
            start = Point3(ox + cos(angle) * 0.02, oy, oz)
            ribbon.setPos(start)
            ribbon.setR(fan)
            ribbon.setScale(Point3(0.4, 1, 0.25))
            ribbon.setBin('fixed', 63)
            ribbon.setDepthTest(False)
            ribbon.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(ribbon)
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + 0.35 + abs(sin(angle)) * 0.28)
        delay = 0.03 * index
        return Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(
                    ribbon, 0.07, Vec4(r, g, b, a), blendType='easeOut'),
                # Squash flat → tall stretch lash (hose pop).
                LerpScaleInterval(
                    ribbon, 0.08, Point3(1.8, 1, 0.35), blendType='easeOut'),
            ),
            LerpScaleInterval(
                ribbon, 0.1, Point3(0.55, 1, 1.55), blendType='easeOut'),
            Parallel(
                LerpPosInterval(ribbon, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    ribbon, sec, Point3(0.2, 1, 0.85), blendType='easeIn'),
                LerpColorScaleInterval(
                    ribbon, sec, Vec4(r, g, b, 0), blendType='easeIn'),
                LerpHprInterval(
                    ribbon, sec, Point3(0, 0, fan + 25 * (1 if index % 2 else -1)),
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
        for np in list(self._nodes):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []


_pop = None


def ensureHandoffConfettiPop():
    global _pop
    if _pop is None:
        _pop = HandoffConfettiPop()
    return _pop


def playHandoffConfetti(origin=None, parent=None):
    """Fire the shared handoff confetti/streamer pop. Returns Sequence or None."""
    return ensureHandoffConfettiPop().play(origin=origin, parent=parent)


def clearHandoffConfetti():
    """Stop/clear any in-flight handoff confetti pop."""
    if _pop is not None:
        _pop.clear()

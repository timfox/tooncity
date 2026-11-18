"""Rubber-hose confetti / streamer juice for campaign handoffs + victory.

Short aspect2d carnival burst when Loopy→Punchline (or act) celebration
fires from CampaignHandoff. Squash/stretch streamers + drifting confetti
bits — Toontown spiritual sequel, never keyblade / KH framing.

Also owns the soft cream confetti swell on campaign victory purity cheer
("TOON CITY IS SAVED!"). That swell clears before the Oswald twist /
FinalePhaseFx reveal so the bittersweet sting stays intact — not a
triumphant second carnival after the truth lands.
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


class VictoryCreamConfettiSwell(object):
    """Soft cream confetti swell on the campaign victory purity cheer.

    Layers a cream flash + expanding ring + cream chips/streamers under the
    "TOON CITY IS SAVED!" plate. Kept separate from HandoffConfettiPop so
    act-handoff carnival bursts and victory cream do not stomp each other.
    Cleared when the victory plate tears down — before Oswald twist /
    FinalePhaseFx reveal — so the truth sting stays bittersweet.
    """

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._flashNP = None
        self._ringNP = None

    def play(self, origin=None, parent=None):
        """Spawn cream swell at `origin` (aspect2d). Returns Sequence or None."""
        if not getattr(CampaignGlobals, 'VICTORY_CREAM_SWELL_ENABLED', True):
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
                CampaignGlobals, 'VICTORY_CREAM_SWELL_ORIGIN',
                (0.0, 0.0, 0.36))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.36

        binSort = int(getattr(CampaignGlobals, 'VICTORY_CREAM_SWELL_BIN', 61))
        parts = []

        flashPart = self._spawnFlash(parentNP, ox, oy, oz, binSort)
        if flashPart is not None:
            parts.append(flashPart)

        ringPart = self._spawnRing(parentNP, ox, oy, oz, binSort)
        if ringPart is not None:
            parts.append(ringPart)

        confettiCount = int(getattr(
            CampaignGlobals, 'VICTORY_CREAM_CONFETTI_COUNT', 14))
        for i in range(confettiCount):
            part = self._spawnConfetti(
                parentNP, ox, oy, oz, i, confettiCount, binSort)
            if part is not None:
                parts.append(part)

        streamerCount = int(getattr(
            CampaignGlobals, 'VICTORY_CREAM_STREAMER_COUNT', 4))
        for i in range(streamerCount):
            part = self._spawnStreamer(
                parentNP, ox, oy, oz, i, streamerCount, binSort)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='campaignVictoryCreamConfettiSwell',
        )
        self._ival.start()
        return self._ival

    def _spawnFlash(self, parentNP, ox, oy, oz, binSort):
        r, g, b, _a = getattr(
            CampaignGlobals, 'VICTORY_CREAM_FLASH_COLOR',
            (1.0, 0.97, 0.84, 1.0))
        peak = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_FLASH_PEAK', 0.28))
        inSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_FLASH_IN_SEC', 0.06))
        holdSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_FLASH_HOLD_SEC', 0.08))
        outSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_FLASH_OUT_SEC', 0.42))
        try:
            cm = CardMaker('victory-cream-flash')
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
            CampaignGlobals, 'VICTORY_CREAM_RING_COLOR',
            (1.0, 0.96, 0.78, 1.0))
        peakScale = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_RING_PEAK', 2.15))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_RING_SEC', 0.55))
        peakA = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_RING_PEAK_ALPHA', 0.42))
        try:
            cm = CardMaker('victory-cream-ring')
            cm.setFrame(-0.55, 0.55, -0.55, 0.55)
            ring = parentNP.attachNewNode(cm.generate())
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, peakA)
            ring.setScale(0.32)
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
            LerpColorScaleInterval(
                ring, max(0.01, sec), Vec4(r, g, b, 0), blendType='easeIn'),
        )

    def _spawnConfetti(self, parentNP, ox, oy, oz, index, total, binSort):
        colors = getattr(
            CampaignGlobals, 'VICTORY_CREAM_CONFETTI_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        size = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_CONFETTI_SIZE', 0.030))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_CONFETTI_DRIFT', 0.78))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_CONFETTI_SEC', 1.05))
        angle = (2.0 * pi * index) / float(max(1, total)) + 0.28
        wide = (index % 2) == 0
        try:
            cm = CardMaker('victory-cream-confetti-%s' % index)
            if wide:
                cm.setFrame(
                    -size * 1.4, size * 1.4, -size * 0.5, size * 0.5)
            else:
                cm.setFrame(
                    -size * 0.5, size * 0.5, -size * 1.3, size * 1.3)
            bit = parentNP.attachNewNode(cm.generate())
            bit.setTransparency(TransparencyAttrib.MAlpha)
            bit.setColor(r, g, b, 1)
            bit.setColorScale(r, g, b, 0)
            start = Point3(
                ox + cos(angle) * 0.05,
                oy,
                oz + sin(angle) * 0.035)
            bit.setPos(start)
            bit.setScale(0.3)
            bit.setR(angle * 35.0)
            bit.setBin('fixed', binSort + 2)
            bit.setDepthTest(False)
            bit.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(bit)
        # Wider outward swell than act-handoff carnival drift.
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + abs(sin(angle)) * drift * 0.9 + 0.08)
        delay = 0.02 * (index % 5)
        return Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(
                    bit, 0.09, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    bit, 0.08, Point3(1.6, 1, 0.42), blendType='easeOut'),
            ),
            LerpScaleInterval(
                bit, 0.1, Point3(0.62, 1, 1.48), blendType='easeOut'),
            Parallel(
                LerpPosInterval(bit, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    bit, sec, Point3(0.12, 1, 0.12), blendType='easeIn'),
                LerpColorScaleInterval(
                    bit, sec, Vec4(r, g, b, 0), blendType='easeIn'),
                LerpHprInterval(
                    bit, sec,
                    Point3(0, 0, bit.getR() + 160 + 35 * (index % 3)),
                    blendType='easeOut'),
            ),
        )

    def _spawnStreamer(self, parentNP, ox, oy, oz, index, total, binSort):
        colors = getattr(
            CampaignGlobals, 'VICTORY_CREAM_STREAMER_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        frame = getattr(
            CampaignGlobals, 'VICTORY_CREAM_STREAMER_FRAME',
            (-0.011, 0.011, -0.10, 0.10))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_STREAMER_DRIFT', 0.88))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_STREAMER_SEC', 1.15))
        fan = -48.0 + (96.0 * index) / float(max(1, total - 1))
        angle = (fan * pi) / 180.0
        try:
            cm = CardMaker('victory-cream-streamer-%s' % index)
            cm.setFrame(*frame)
            ribbon = parentNP.attachNewNode(cm.generate())
            ribbon.setTransparency(TransparencyAttrib.MAlpha)
            ribbon.setColor(r, g, b, 1)
            ribbon.setColorScale(r, g, b, 0)
            start = Point3(ox + cos(angle) * 0.02, oy, oz)
            ribbon.setPos(start)
            ribbon.setR(fan)
            ribbon.setScale(Point3(0.35, 1, 0.22))
            ribbon.setBin('fixed', binSort + 1)
            ribbon.setDepthTest(False)
            ribbon.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(ribbon)
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + 0.42 + abs(sin(angle)) * 0.32)
        delay = 0.035 * index
        return Sequence(
            Wait(delay),
            Parallel(
                LerpColorScaleInterval(
                    ribbon, 0.08, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    ribbon, 0.09, Point3(1.7, 1, 0.32), blendType='easeOut'),
            ),
            LerpScaleInterval(
                ribbon, 0.11, Point3(0.5, 1, 1.6), blendType='easeOut'),
            Parallel(
                LerpPosInterval(ribbon, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    ribbon, sec, Point3(0.18, 1, 0.8), blendType='easeIn'),
                LerpColorScaleInterval(
                    ribbon, sec, Vec4(r, g, b, 0), blendType='easeIn'),
                LerpHprInterval(
                    ribbon, sec,
                    Point3(0, 0, fan + 22 * (1 if index % 2 else -1)),
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


_swell = None


def ensureVictoryCreamConfettiSwell():
    global _swell
    if _swell is None:
        _swell = VictoryCreamConfettiSwell()
    return _swell


def playVictoryCreamSwell(origin=None, parent=None):
    """Fire the victory cream confetti swell. Returns Sequence or None."""
    return ensureVictoryCreamConfettiSwell().play(
        origin=origin, parent=parent)


def clearVictoryCreamSwell():
    """Stop/clear any in-flight victory cream confetti swell."""
    if _swell is not None:
        _swell.clear()

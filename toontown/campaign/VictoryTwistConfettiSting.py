"""Short victory/confetti sting on Oswald finale twist (betrayal handoff).

After Silly finale purity cheer (#82 cream swell clears) and the betrayal
handoff banner (#212) hose-pops the twist copy, this fires a quieter,
bittersweet confetti sting — cream + warm coral chips that land the truth
that Oswald caused the corruption. Not a second triumphant carnival; not
the sunny victory cream swell. Toontown spiritual-sequel tone only —
no keyblades / KH branding.
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


class VictoryTwistConfettiSting(object):
    """Owns one short bittersweet confetti sting under the twist plate."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._flashNP = None

    def play(self, origin=None, parent=None):
        """Spawn twist confetti sting. Returns started Sequence or None."""
        if not getattr(
                CampaignGlobals, 'VICTORY_TWIST_CONFETTI_ENABLED', True):
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
                CampaignGlobals, 'VICTORY_TWIST_CONFETTI_ORIGIN',
                (0.0, 0.0, 0.34))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.34

        binSort = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_BIN', 62))
        delay = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_DELAY_SEC', 0.18))
        parts = []

        flashPart = self._spawnFlash(parentNP, ox, oy, oz, binSort)
        if flashPart is not None:
            parts.append(flashPart)

        confettiCount = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_COUNT', 9))
        for i in range(confettiCount):
            part = self._spawnConfetti(
                parentNP, ox, oy, oz, i, confettiCount, binSort)
            if part is not None:
                parts.append(part)

        streakCount = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_COUNT', 3))
        for i in range(streakCount):
            part = self._spawnStreak(
                parentNP, ox, oy, oz, i, streakCount, binSort)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        self._ival = Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
            Func(self.clear),
            name='campaignVictoryTwistConfettiSting',
        )
        self._ival.start()
        return self._ival

    def _spawnFlash(self, parentNP, ox, oy, oz, binSort):
        r, g, b, _a = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_COLOR',
            (1.0, 0.88, 0.72, 1.0))
        peak = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_PEAK', 0.16))
        inSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_IN_SEC', 0.05))
        holdSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_HOLD_SEC', 0.05))
        outSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_OUT_SEC', 0.36))
        try:
            cm = CardMaker('victory-twist-confetti-flash')
            cm.setFrame(-1.8, 1.8, -1.6, 1.6)
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

    def _spawnConfetti(self, parentNP, ox, oy, oz, index, total, binSort):
        colors = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        size = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_SIZE', 0.024))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_DRIFT', 0.48))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_SEC', 0.72))
        # Slight downward settle bias — hollow victory, not carnival lift.
        fall = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FALL', 0.18))
        angle = (2.0 * pi * index) / float(max(1, total)) + 0.42
        wide = (index % 2) == 0
        try:
            cm = CardMaker('victory-twist-confetti-%s' % index)
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
                oz + sin(angle) * 0.028)
            bit.setPos(start)
            bit.setScale(0.28)
            bit.setR(angle * 32.0)
            bit.setBin('fixed', binSort + 2)
            bit.setDepthTest(False)
            bit.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(bit)
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + abs(sin(angle)) * drift * 0.45 - fall)
        chipDelay = 0.018 * (index % 4)
        return Sequence(
            Wait(chipDelay),
            Parallel(
                LerpColorScaleInterval(
                    bit, 0.07, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    bit, 0.07, Point3(1.45, 1, 0.48), blendType='easeOut'),
            ),
            LerpScaleInterval(
                bit, 0.08, Point3(0.7, 1, 1.32), blendType='easeOut'),
            Parallel(
                LerpPosInterval(bit, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    bit, sec, Point3(0.1, 1, 0.1), blendType='easeIn'),
                LerpColorScaleInterval(
                    bit, sec, Vec4(r, g, b, 0), blendType='easeIn'),
                LerpHprInterval(
                    bit, sec,
                    Point3(0, 0, bit.getR() + 120 + 28 * (index % 3)),
                    blendType='easeOut'),
            ),
        )

    def _spawnStreak(self, parentNP, ox, oy, oz, index, total, binSort):
        """Thin cream/coral streak glitter — quieter than victory sparkle."""
        colors = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_COLORS', ())
        if not colors:
            return None
        r, g, b, a = colors[index % len(colors)]
        size = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_SIZE', 0.012))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_DRIFT', 0.38))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_SEC', 0.58))
        fall = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FALL', 0.18))
        angle = (2.0 * pi * index) / float(max(1, total)) + 0.55
        try:
            cm = CardMaker('victory-twist-confetti-streak-%s' % index)
            cm.setFrame(
                -size * 0.3, size * 0.3, -size * 1.5, size * 1.5)
            streak = parentNP.attachNewNode(cm.generate())
            streak.setTransparency(TransparencyAttrib.MAlpha)
            streak.setColor(r, g, b, 1)
            streak.setColorScale(r, g, b, 0)
            start = Point3(
                ox + cos(angle) * 0.03,
                oy,
                oz + sin(angle) * 0.02)
            streak.setPos(start)
            streak.setScale(0.25)
            streak.setR(angle * 40.0)
            streak.setBin('fixed', binSort + 3)
            streak.setDepthTest(False)
            streak.setDepthWrite(False)
        except Exception:
            return None

        self._nodes.append(streak)
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + abs(sin(angle)) * drift * 0.35 - fall * 0.7)
        return Sequence(
            Wait(0.03 * index),
            Parallel(
                LerpColorScaleInterval(
                    streak, 0.06, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    streak, 0.06, Point3(1.2, 1, 1.4), blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(streak, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    streak, sec, Point3(0.08, 1, 0.08), blendType='easeIn'),
                LerpColorScaleInterval(
                    streak, sec, Vec4(r, g, b, 0), blendType='easeIn'),
            ),
        )

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._flashNP is not None:
            try:
                if not self._flashNP.isEmpty():
                    self._flashNP.removeNode()
            except Exception:
                pass
            self._flashNP = None
        for np in list(self._nodes):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []


_sting = None


def ensureVictoryTwistConfettiSting():
    global _sting
    if _sting is None:
        _sting = VictoryTwistConfettiSting()
    return _sting


def playVictoryTwistConfettiSting(origin=None, parent=None):
    """Fire the Oswald-twist victory confetti sting. Returns Sequence or None."""
    return ensureVictoryTwistConfettiSting().play(
        origin=origin, parent=parent)


def clearVictoryTwistConfettiSting():
    """Stop/clear any in-flight twist confetti sting."""
    if _sting is not None:
        _sting.clear()

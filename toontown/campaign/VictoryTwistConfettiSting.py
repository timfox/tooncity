"""Deepened victory/confetti cream sting on Oswald finale twist.

After Silly finale purity cheer (#82 cream swell clears) and the betrayal
handoff banner (#212) hose-pops the twist copy, this fires a juicier,
bittersweet confetti sting past #244 — cream + warm coral chips with a
micro cream pop rebound and richer soft cream aftershock so the hollow
cheer that Oswald caused the corruption lands readable. Not a second
triumphant carnival; not the sunny victory cream swell. Distinct from act
handoff cream edge settle deepen (#240) and betrayal banner cream hose
deepen (#235 / #260). Toontown spiritual-sequel tone only — no keyblades
/ KH branding.
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
    """Owns one deepened (past #244) bittersweet confetti cream sting."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._flashNP = None
        self._haloNP = None

    def play(self, origin=None, parent=None):
        """Spawn deepened twist confetti sting. Returns started Sequence or None."""
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
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_BIN', 61))
        delay = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_DELAY_SEC', 0.16))
        parts = []

        flashPart = self._spawnFlash(parentNP, ox, oy, oz, binSort)
        if flashPart is not None:
            parts.append(flashPart)

        confettiCount = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_COUNT', 12))
        for i in range(confettiCount):
            part = self._spawnConfetti(
                parentNP, ox, oy, oz, i, confettiCount, binSort)
            if part is not None:
                parts.append(part)

        streakCount = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_COUNT', 4))
        for i in range(streakCount):
            part = self._spawnStreak(
                parentNP, ox, oy, oz, i, streakCount, binSort)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        stingBody = Parallel(*parts)
        aftershock = self._buildAftershock(parentNP, ox, oy, oz)
        if aftershock is not None:
            body = Parallel(stingBody, aftershock)
        else:
            body = stingBody

        self._ival = Sequence(
            Wait(max(0.0, delay)),
            body,
            Func(self.clear),
            name='campaignVictoryTwistConfettiSting',
        )
        self._ival.start()
        return self._ival

    def _spawnFlash(self, parentNP, ox, oy, oz, binSort):
        r, g, b, _a = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_COLOR',
            (1.0, 0.90, 0.74, 1.0))
        peak = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_PEAK', 0.20))
        inSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_IN_SEC', 0.05))
        holdSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_HOLD_SEC', 0.06))
        outSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FLASH_OUT_SEC', 0.42))
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
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_SIZE', 0.027))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_DRIFT', 0.56))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_SEC', 0.82))
        # Slight downward settle bias — hollow victory, not carnival lift.
        fall = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FALL', 0.22))
        pop = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_POP', 1.72))
        rebound = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_POP_REBOUND', 1.22))
        reboundSec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_POP_REBOUND_SEC', 0.05))
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
        chipDelay = 0.016 * (index % 4)
        # Juicier cream snap past #244: squash → stretch → micro rebound → settle.
        squashPt = Point3(pop, 1, max(0.35, 2.0 - pop * 0.65))
        stretchPt = Point3(max(0.55, 2.05 - pop * 0.55), 1, pop * 0.84)
        reboundPt = Point3(
            max(0.7, rebound), 1, max(0.7, rebound * 0.92))
        return Sequence(
            Wait(chipDelay),
            Parallel(
                LerpColorScaleInterval(
                    bit, 0.07, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    bit, 0.07, squashPt, blendType='easeOut'),
            ),
            LerpScaleInterval(
                bit, 0.08, stretchPt, blendType='easeOut'),
            LerpScaleInterval(
                bit, max(0.01, reboundSec), reboundPt, blendType='easeOut'),
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
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_SIZE', 0.014))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_DRIFT', 0.44))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_STREAK_SEC', 0.66))
        fall = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_FALL', 0.22))
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
            Wait(0.028 * index),
            Parallel(
                LerpColorScaleInterval(
                    streak, 0.06, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    streak, 0.06, Point3(1.36, 1, 1.58), blendType='easeOut'),
            ),
            LerpScaleInterval(
                streak, 0.04, Point3(1.12, 1, 1.22), blendType='easeOut'),
            Parallel(
                LerpPosInterval(streak, sec, end, blendType='easeOut'),
                LerpScaleInterval(
                    streak, sec, Point3(0.08, 1, 0.08), blendType='easeIn'),
                LerpColorScaleInterval(
                    streak, sec, Vec4(r, g, b, 0), blendType='easeIn'),
            ),
        )

    def _buildAftershock(self, parentNP, ox, oy, oz):
        """Richer cream settle flecks (+ optional halo) after sting body."""
        if not getattr(
                CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_ENABLED',
                True):
            return None
        delay = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_DELAY_SEC',
            0.18))
        parts = []

        if getattr(
                CampaignGlobals,
                'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_COUNT', 7))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_SEC', 0.40))
        for i in range(count):
            part = self._spawnAftershockFleck(
                parentNP, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parentNP, ox, oy, oz):
        half = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_HALF',
            0.46))
        startScale = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_START',
            0.24))
        peakScale = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_PEAK',
            1.30))
        sec = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_SEC',
            0.34))
        peakA = float(getattr(
            CampaignGlobals,
            'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_PEAK_ALPHA', 0.16))
        r, g, b, _a = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.93, 0.76, 1.0))
        binSort = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_BIN', 60))
        try:
            cm = CardMaker('victory-twist-confetti-aftershock-halo')
            # Soft oval under betrayal plate — quieter than victory wash halo.
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(ox, oy, oz)
            halo.setScale(startScale)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
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

    def _spawnAftershockFleck(self, parentNP, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual sting aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_SIZE', 0.019))
        drift = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_DRIFT', 0.36))
        fall = float(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_FALL', 0.28))
        r, g, b, a = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_COLOR',
            (1.0, 0.96, 0.78, 0.88))
        er, eg, eb, ea = getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_END_COLOR',
            (1.0, 0.88, 0.52, 0.0))
        binSort = int(getattr(
            CampaignGlobals, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_BIN', 60))
        angle = (2.0 * pi * index) / float(count) + 0.41
        try:
            cm = CardMaker('victory-twist-confetti-aftershock-%s' % index)
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.07
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.26 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.05 * (index % 3))
        peak = 1.04 + 0.06 * (index % 2)
        self._nodes.append(fleck)
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.28), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.72), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.72), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
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
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
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
    """Fire the deepened Oswald-twist victory confetti cream sting."""
    return ensureVictoryTwistConfettiSting().play(
        origin=origin, parent=parent)


def clearVictoryTwistConfettiSting():
    """Stop/clear any in-flight twist confetti sting."""
    if _sting is not None:
        _sting.clear()

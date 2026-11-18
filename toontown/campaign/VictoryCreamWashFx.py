"""Rubber-hose cream wash pulse after victory cream edge / sparkle.

Fullscreen soft cream veil that settles *after* victory cream confetti
swell (#82), cream sparkle (#105), and cream edge (#129) — same
PerfectDodgeCreamWashPulse / HitSparkCreamWashPulse / HandoffCreamWashPulse
/ OswaldTrustCreamWashPulse / FinaleRevealCreamWashPulse overlay grammar
as a brief purity-cheer settle beat. Soft under the victory plate + edge
strips; cream / pastel only (not ink). Wired from CampaignHandoff
creamSwell (victory path only) beside the cream edge. Act-enter wash
lives in ActBannerCreamWashFx; handoff carnival wash lives in
HandoffCreamWashFx; Oswald trust wash lives in OswaldTrustCreamWashFx;
finale-reveal wash lives in FinaleRevealCreamWashFx. Clears before
Oswald twist / FinalePhaseFx reveal. Client only. Toontown spiritual
sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.campaign import CampaignGlobals


class VictoryCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after victory cream edge."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'VICTORY_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(CampaignGlobals, 'VICTORY_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_PEAK', 0.16))
        mid = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_MID', 0.09))
        inSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_OUT_SEC', 0.48))
        binSort = int(getattr(
            CampaignGlobals, 'VICTORY_CREAM_WASH_BIN', 54))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'VICTORY_CREAM_WASH_DELAY_SEC', 0.48))

        try:
            cm = CardMaker('campaign-victory-cream-wash')
            # Full-frame veil — melee / perfect-dodge / entry wash grammar.
            cm.setFrame(-2, 2, -2, 2)
            wash = parent.attachNewNode(cm.generate())
            wash.setTransparency(TransparencyAttrib.MAlpha)
            wash.setColor(r, g, b, 1)
            wash.setColorScale(r, g, b, 0)
            wash.setBin('fixed', binSort)
            wash.setDepthTest(False)
            wash.setDepthWrite(False)
            self._washNP = wash
        except Exception:
            self._washNP = None
            return None

        # Delayed two-beat after cream edge / sparkle: bright → settle → fade.
        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            LerpColorScaleInterval(
                wash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            LerpColorScaleInterval(
                wash, max(0.01, pulseSec), Vec4(r, g, b, mid),
                blendType='easeInOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                wash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
            Func(self.clear),
            name='campaignVictoryCreamWash',
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
        wash = self._washNP
        self._washNP = None
        if wash is None:
            return
        try:
            if not wash.isEmpty():
                wash.removeNode()
        except Exception:
            pass


_victoryWashFx = None


def _getVictoryWashFx():
    global _victoryWashFx
    if _victoryWashFx is None:
        _victoryWashFx = VictoryCreamWashPulse()
    return _victoryWashFx


def playVictoryCreamWash(delay=None):
    """Fire soft cream wash pulse on victory cream edge / sparkle cheer."""
    return _getVictoryWashFx().play(delay=delay)


def clearVictoryCreamWash():
    """Tear down any in-flight victory cream wash pulse."""
    if _victoryWashFx is not None:
        _victoryWashFx.clear()

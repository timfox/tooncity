"""Rubber-hose cream wash pulse after handoff cream edge / sparkle.

Fullscreen soft cream veil that settles *after* hood handoff cream-sparkle
carnival (#99) and cream edge (#124) — same PerfectDodgeCreamWashPulse /
HitSparkCreamWashPulse / VictoryCreamWashPulse / OswaldTrustCreamWashPulse
/ FinaleRevealCreamWashPulse overlay grammar as a brief act-handoff settle
beat. Soft under the handoff plate + edge strips; cream / pastel only (not
ink). Wired from CampaignHandoff confetti (act handoff path only) beside
the cream edge. Oswald trust wash lives in OswaldTrustCreamWashFx;
finale-reveal wash lives in FinaleRevealCreamWashFx; phase stays
wash-free here. Client only. Toontown spiritual sequel — no keyblades /
no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.campaign import CampaignGlobals


class HandoffCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after handoff cream edge."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'HANDOFF_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(CampaignGlobals, 'HANDOFF_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_PEAK', 0.14))
        mid = float(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_MID', 0.08))
        inSec = float(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_OUT_SEC', 0.40))
        binSort = int(getattr(
            CampaignGlobals, 'HANDOFF_CREAM_WASH_BIN', 54))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'HANDOFF_CREAM_WASH_DELAY_SEC', 0.40))

        try:
            cm = CardMaker('campaign-handoff-cream-wash')
            # Full-frame veil — melee / perfect-dodge / victory wash grammar.
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
            name='campaignHandoffCreamWash',
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


_handoffWashFx = None


def _getHandoffWashFx():
    global _handoffWashFx
    if _handoffWashFx is None:
        _handoffWashFx = HandoffCreamWashPulse()
    return _handoffWashFx


def playHandoffCreamWash(delay=None):
    """Fire soft cream wash pulse on handoff cream edge / sparkle carnival."""
    return _getHandoffWashFx().play(delay=delay)


def clearHandoffCreamWash():
    """Tear down any in-flight handoff cream wash pulse."""
    if _handoffWashFx is not None:
        _handoffWashFx.clear()

"""Rubber-hose cream wash pulse after act-enter banner cream edge.

Fullscreen soft cream veil that settles *after* PlayEntry act-enter hose
pop (#70) and cream edge (#110) — same PerfectDodgeCreamWashPulse /
HitSparkCreamWashPulse / OswaldTrustCreamWashPulse / HandoffCreamWashPulse
/ VictoryCreamWashPulse / FinaleRevealCreamWashPulse overlay grammar as a
brief act-enter settle beat. Soft under the act banner + edge strips;
cream / pastel only (not ink). Wired from PlayEntry creamEdge act-enter
path only, beside the cream edge. Reclaim cue flashes stay wash-free.
Punchline tip wash lives in PunchlineTipCreamWashFx; trust / handoff /
victory / finale-reveal wash live in their own modules. Client only.
Toontown spiritual sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.campaign import CampaignGlobals


class ActBannerCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after act-banner cream edge."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_PEAK', 0.12))
        mid = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_MID', 0.07))
        inSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_OUT_SEC', 0.36))
        binSort = int(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_BIN', 49))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_WASH_DELAY_SEC',
                0.36))

        try:
            cm = CardMaker('campaign-act-banner-cream-wash')
            # Full-frame veil — trust / handoff / victory wash grammar.
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

        # Delayed two-beat after cream edge: bright → settle → fade.
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
            name='campaignActBannerCreamWash',
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


_actBannerWashFx = None


def _getActBannerWashFx():
    global _actBannerWashFx
    if _actBannerWashFx is None:
        _actBannerWashFx = ActBannerCreamWashPulse()
    return _actBannerWashFx


def playActBannerCreamWash(delay=None):
    """Fire soft cream wash pulse on act-enter banner cream edge."""
    return _getActBannerWashFx().play(delay=delay)


def clearActBannerCreamWash():
    """Tear down any in-flight act-banner cream wash pulse."""
    if _actBannerWashFx is not None:
        _actBannerWashFx.clear()

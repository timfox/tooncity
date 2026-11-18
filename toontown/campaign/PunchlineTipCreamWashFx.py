"""Rubber-hose cream wash pulse after Punchline Act 2 tip hose pop.

Fullscreen soft cream veil that settles *after* Punchline Place entry tip
hose pop (#91) and deepened cream hose settle past #256 — same
PerfectDodgeCreamWashPulse / HitSparkCreamWashPulse /
ActBannerCreamWashPulse / OswaldTrustCreamWashPulse / HandoffCreamWashPulse
/ VictoryCreamWashPulse / FinaleRevealCreamWashPulse overlay grammar as a
brief Act-2 tip settle beat. Soft under the tip bar; cream / pastel only
(not ink). Wash delay / peak ride the juicier tip hose settle. Wired from
PlayEntry tipHose='punchline' path only. Loopy / default tip hose stay
wash-free; Silly tip wash lives in SillyTipCreamWashFx; act-enter banner
wash, trust / handoff / victory / finale-reveal wash live in their own
modules. Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.campaign import CampaignGlobals


class PunchlineTipCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after Punchline tip hose pop."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_PEAK', 0.13))
        mid = float(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_MID', 0.08))
        inSec = float(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_IN_SEC', 0.08))
        pulseSec = float(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_PULSE_SEC', 0.13))
        holdSec = float(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_HOLD_SEC', 0.12))
        outSec = float(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_OUT_SEC', 0.40))
        binSort = int(getattr(
            CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_BIN', 49))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'PUNCHLINE_ACT_TIP_CREAM_WASH_DELAY_SEC',
                0.70))

        try:
            cm = CardMaker('campaign-punchline-tip-cream-wash')
            # Full-frame veil — act-banner / trust / handoff wash grammar.
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

        # Delayed two-beat after tip hose pop: bright → settle → fade.
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
            name='campaignPunchlineTipCreamWash',
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


_punchlineTipWashFx = None


def _getPunchlineTipWashFx():
    global _punchlineTipWashFx
    if _punchlineTipWashFx is None:
        _punchlineTipWashFx = PunchlineTipCreamWashPulse()
    return _punchlineTipWashFx


def playPunchlineTipCreamWash(delay=None):
    """Fire soft cream wash pulse on Punchline Act 2 tip hose pop."""
    return _getPunchlineTipWashFx().play(delay=delay)


def clearPunchlineTipCreamWash():
    """Tear down any in-flight Punchline tip cream wash pulse."""
    if _punchlineTipWashFx is not None:
        _punchlineTipWashFx.clear()

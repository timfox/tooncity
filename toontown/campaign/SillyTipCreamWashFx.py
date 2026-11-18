"""Rubber-hose cream wash pulse after Silly Act 3 tip hose pop.

Fullscreen soft cream veil that settles *after* Silly Street entry tip
hose pop (#95) — same PerfectDodgeCreamWashPulse / HitSparkCreamWashPulse /
ActBannerCreamWashPulse / OswaldTrustCreamWashPulse / HandoffCreamWashPulse
/ VictoryCreamWashPulse / FinaleRevealCreamWashPulse /
PunchlineTipCreamWashPulse overlay grammar as a brief Act-3 tip settle
beat. Soft under the tip bar; cream / pastel only (not ink). Wired from
PlayEntry tipHose='silly' path only. Loopy / Punchline / default tip hose,
act-enter banner wash, trust / handoff / victory / finale-reveal wash live
in their own modules. Client only. Toontown spiritual sequel — no
keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.campaign import CampaignGlobals


class SillyTipCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after Silly tip hose pop."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_PEAK', 0.12))
        mid = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_MID', 0.07))
        inSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_OUT_SEC', 0.36))
        binSort = int(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_BIN', 49))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_DELAY_SEC',
                0.36))

        try:
            cm = CardMaker('campaign-silly-tip-cream-wash')
            # Full-frame veil — act-banner / trust / Punchline tip wash grammar.
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
            name='campaignSillyTipCreamWash',
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


_sillyTipWashFx = None


def _getSillyTipWashFx():
    global _sillyTipWashFx
    if _sillyTipWashFx is None:
        _sillyTipWashFx = SillyTipCreamWashPulse()
    return _sillyTipWashFx


def playSillyTipCreamWash(delay=None):
    """Fire soft cream wash pulse on Silly Act 3 tip hose pop."""
    return _getSillyTipWashFx().play(delay=delay)


def clearSillyTipCreamWash():
    """Tear down any in-flight Silly tip cream wash pulse."""
    if _sillyTipWashFx is not None:
        _sillyTipWashFx.clear()

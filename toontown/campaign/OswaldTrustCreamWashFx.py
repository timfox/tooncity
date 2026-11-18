"""Rubber-hose cream wash pulse after Oswald trust banner cream edge.

Fullscreen soft cream veil that settles *after* early/mid Oswald trust
hose settle (#76) and cream edge (#117) — same PerfectDodgeCreamWashPulse /
HitSparkCreamWashPulse / HandoffCreamWashPulse / VictoryCreamWashPulse /
FinaleRevealCreamWashPulse overlay grammar as a brief trusted-hero settle
beat. Soft under the trust plate + edge strips; cream / pastel only (not
ink). Wired from CampaignHandoff trustSettle (Oswald trusted early/mid
only) beside the cream edge. No carnival / no twist spoilers — act-enter
wash lives in ActBannerCreamWashFx; Punchline tip wash lives in
PunchlineTipCreamWashFx; Silly tip wash lives in SillyTipCreamWashFx;
twist / victory / phase / handoff carnival stay on their own wash
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


class OswaldTrustCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after trust cream edge."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_PEAK', 0.12))
        mid = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_MID', 0.07))
        inSec = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_OUT_SEC', 0.36))
        binSort = int(getattr(
            CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_BIN', 54))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'OSWALD_TRUST_BANNER_CREAM_WASH_DELAY_SEC',
                0.36))

        try:
            cm = CardMaker('campaign-oswald-trust-cream-wash')
            # Full-frame veil — handoff / victory / melee wash grammar.
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
            name='campaignOswaldTrustCreamWash',
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


_trustWashFx = None


def _getTrustWashFx():
    global _trustWashFx
    if _trustWashFx is None:
        _trustWashFx = OswaldTrustCreamWashPulse()
    return _trustWashFx


def playOswaldTrustCreamWash(delay=None):
    """Fire soft cream wash pulse on Oswald trust banner cream edge."""
    return _getTrustWashFx().play(delay=delay)


def clearOswaldTrustCreamWash():
    """Tear down any in-flight Oswald trust cream wash pulse."""
    if _trustWashFx is not None:
        _trustWashFx.clear()

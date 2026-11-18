"""Rubber-hose cream wash pulse + delayed cream aftershock on Silly tip.

Fullscreen soft cream veil that settles *after* Silly Street entry tip
hose pop (#95) / Overlord foreshadow / Oswald almost-confess tip (#200 /
#251 deepen) — same PerfectDodgeCreamWashPulse / HitSparkCreamWashPulse /
ActBannerCreamWashPulse / OswaldTrustCreamWashPulse / HandoffCreamWashPulse
/ VictoryCreamWashPulse / FinaleRevealCreamWashPulse /
PunchlineTipCreamWashPulse overlay grammar as a brief Act-3 tip settle
beat. A delayed cream aftershock (richer flecks settling downward + soft
halo under the tip bar) follows the wash pulse — same residual grammar as
Oswald trust cream wash aftershock (#170) / victory cream wash aftershock
(#168), quieter and tip-bar anchored so the almost-confess / foreshadow tip
reads juicier before the boss (deepened past #251). Soft under the tip bar;
cream / pastel only (not ink). Wired from PlayEntry tipHose='silly' path
only. Distinct from victory twist sting cream deepen (#244) and betrayal
banner cream hose settle (#235); hose settle deepen (#232 / past) stays on
the tip bar scale path. Loopy / Punchline / default tip hose, act-enter
banner wash, trust / handoff / victory / finale-reveal wash live in their
own modules. Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from math import cos, pi

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from toontown.campaign import CampaignGlobals


class SillyTipCreamWashPulse(object):
    """Owns cream wash pulse + delayed fleck/halo aftershock on Silly tip."""

    def __init__(self):
        self._ival = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash + aftershock. Returns Sequence or None."""
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
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_PEAK', 0.15))
        mid = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_MID', 0.09))
        inSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_PULSE_SEC', 0.13))
        holdSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_HOLD_SEC', 0.14))
        outSec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_OUT_SEC', 0.44))
        binSort = int(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_BIN', 49))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_DELAY_SEC',
                0.62))

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
        washVeil = Sequence(
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
            name='campaignSillyTipCreamWashVeil',
        )

        origin = getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ORIGIN',
            (0.0, 0.0, -0.72))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.72

        aftershock = self._buildAftershock(parent, ox, oy, oz)
        beat = washVeil
        if aftershock is not None:
            # Wash lifetime rides beside residual flecks / halo.
            beat = Parallel(washVeil, aftershock)

        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            beat,
            Func(self.clear),
            name='campaignSillyTipCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after Silly tip wash."""
        if not getattr(
                CampaignGlobals,
                'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            CampaignGlobals,
            'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.18))
        parts = []

        if getattr(
                CampaignGlobals,
                'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SEC', 0.36))
        for i in range(count):
            part = self._spawnAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_HALF',
            0.40))
        startScale = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_START',
            0.26))
        peakScale = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_PEAK',
            1.18))
        sec = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_SEC',
            0.30))
        peakA = float(getattr(
            CampaignGlobals,
            'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.13))
        r, g, b, _a = getattr(
            CampaignGlobals,
            'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_BIN', 51))
        try:
            cm = CardMaker('campaign-silly-tip-cream-wash-aftershock-halo')
            # Soft oval halo under tip bar — quieter residual of foreshadow wash.
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parent.attachNewNode(cm.generate())
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

    def _spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual tip wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SIZE',
            0.016))
        drift = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_DRIFT',
            0.28))
        fall = float(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_FALL',
            0.21))
        r, g, b, a = getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.76))
        er, eg, eb, ea = getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            CampaignGlobals, 'SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_BIN', 51))
        angle = (2.0 * pi * index) / float(count) + 0.27
        try:
            cm = CardMaker(
                'campaign-silly-tip-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the tip cream wash.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.07
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.26 + 0.07 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream under tip bar, not victory glitter rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.03 * (index % 3))
        peak = 1.04 + 0.07 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.014 * (index % 3)
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
        """Stop wash/aftershock and remove every Silly tip cream wash node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._washNP
        self._washNP = None
        if wash is not None:
            try:
                if not wash.isEmpty():
                    wash.removeNode()
            except Exception:
                pass
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._fleckNPs:
            if np is not None:
                try:
                    if not np.isEmpty():
                        np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []


_sillyTipWashFx = None


def _getSillyTipWashFx():
    global _sillyTipWashFx
    if _sillyTipWashFx is None:
        _sillyTipWashFx = SillyTipCreamWashPulse()
    return _sillyTipWashFx


def playSillyTipCreamWash(delay=None):
    """Fire soft cream wash pulse + aftershock on Silly Act 3 tip hose pop."""
    return _getSillyTipWashFx().play(delay=delay)


def clearSillyTipCreamWash():
    """Tear down any in-flight Silly tip cream wash pulse / aftershock."""
    if _sillyTipWashFx is not None:
        _sillyTipWashFx.clear()

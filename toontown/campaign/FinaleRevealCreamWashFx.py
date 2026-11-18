"""Rubber-hose cream wash pulse + delayed cream aftershock on finale reveal.

Fullscreen soft cream veil that settles *after* Oswald-twist cream
aftershock (#86) and cream edge (#133) — same PerfectDodgeCreamWashPulse /
HitSparkCreamWashPulse / OswaldTrustCreamWashPulse / HandoffCreamWashPulse
/ VictoryCreamWashPulse overlay grammar as a brief residual settle beat
under held twist copy. A delayed cream aftershock (softer flecks settling
downward + soft halo) follows the wash pulse — same residual grammar as
victory cream wash aftershock (#168) / reclaim entry cream wash aftershock
(#132) / purity-complete cream aftershock (#136). Soft under the reveal
edge strips; cream / pastel only (not ink). Wired from FinalePhaseFx cream
aftershock arm (Oswald-twist path only) beside the cream edge. Act-enter /
Punchline tip / Silly tip / trust / handoff / victory wash live in their
own modules. Supports the twist without undoing it or replaying victory
cheer wash / aftershock. Client only. Toontown spiritual sequel — no
keyblades / no KH branding.
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


class FinaleRevealCreamWashPulse(object):
    """Owns cream wash pulse + delayed fleck/halo aftershock on reveal."""

    def __init__(self):
        self._ival = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash + aftershock. Returns Sequence or None."""
        if not getattr(
                CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_PEAK', 0.13))
        mid = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_MID', 0.07))
        inSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_IN_SEC', 0.07))
        pulseSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_PULSE_SEC', 0.12))
        holdSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_OUT_SEC', 0.42))
        binSort = int(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_BIN', 54))
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_DELAY_SEC', 0.40))

        try:
            cm = CardMaker('campaign-finale-reveal-cream-wash')
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

        # Delayed two-beat after cream edge / aftershock: bright → settle → fade.
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
            name='campaignFinaleRevealCreamWashVeil',
        )

        origin = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ORIGIN',
            (0.0, 0.0, 0.08))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.08

        aftershock = self._buildAftershock(parent, ox, oy, oz)
        beat = washVeil
        if aftershock is not None:
            # Wash lifetime rides beside residual flecks / halo.
            beat = Parallel(washVeil, aftershock)

        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            beat,
            Func(self.clear),
            name='campaignFinaleRevealCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after reveal wash."""
        if not getattr(
                CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ENABLED',
                True):
            return None
        delay = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
            0.22))
        parts = []

        if getattr(
                CampaignGlobals,
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_COUNT', 6))
        sec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_SEC', 0.36))
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
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_HALF',
            0.48))
        startScale = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_START',
            0.28))
        peakScale = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_PEAK',
            1.18))
        sec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_SEC',
            0.30))
        peakA = float(getattr(
            CampaignGlobals,
            'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.13))
        r, g, b, _a = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_BIN', 55))
        try:
            cm = CardMaker('campaign-finale-reveal-cream-wash-aftershock-halo')
            # Soft oval halo under twist copy — quieter residual of wash.
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
        """Softer cream chip that settles downward — residual wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_SIZE',
            0.016))
        drift = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_DRIFT',
            0.30))
        fall = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_FALL',
            0.24))
        r, g, b, a = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.78))
        er, eg, eb, ea = getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_BIN', 55))
        angle = (2.0 * pi * index) / float(count) + 0.31
        try:
            cm = CardMaker(
                'campaign-finale-reveal-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the cream wash.
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
            startX = ox + cos(angle) * 0.08
            startZ = oz + 0.014 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream, not edge sparkle's outward rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.04 * (index % 3))
        peak = 1.05 + 0.08 * (index % 2)
        self._fleckNPs.append(fleck)
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
        """Stop wash/aftershock and remove every finale reveal cream wash node."""
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


_finaleRevealWashFx = None


def _getFinaleRevealWashFx():
    global _finaleRevealWashFx
    if _finaleRevealWashFx is None:
        _finaleRevealWashFx = FinaleRevealCreamWashPulse()
    return _finaleRevealWashFx


def playFinaleRevealCreamWash(delay=None):
    """Fire soft cream wash pulse + aftershock on finale reveal."""
    return _getFinaleRevealWashFx().play(delay=delay)


def clearFinaleRevealCreamWash():
    """Tear down any in-flight finale reveal cream wash pulse / aftershock."""
    if _finaleRevealWashFx is not None:
        _finaleRevealWashFx.clear()

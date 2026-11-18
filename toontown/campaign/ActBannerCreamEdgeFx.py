"""Rubber-hose cream edge pulse for campaign banners.

Soft cream border strips + tip flecks that frame:
  * PlayEntry act-enter flash banners (#70 hose pop) — #110
  * Early/mid Oswald trust handoff banners (#76 hose settle) — #117
  * Mid-act Oswald trust fracture (Loopy clear) — cool cream → shadow flecks
  * Hood handoff cream-sparkle carnival banners (#99) — #124
  * Victory cream confetti / sparkle banners (#82/#105) — #129
  * Finale reveal cream aftershock banners (#86) — TC-136

Handoff / victory / finale-reveal cream-sparkle paths also rise cream
sparkle flecks along the cream frame (wave-edge #113 twin). Act-enter,
Oswald trust settle, handoff carnival, victory cheer, and finale reveal
also arm a delayed soft cream wash pulse (ActBannerCreamWashFx /
OswaldTrustCreamWashFx / HandoffCreamWashFx / VictoryCreamWashFx /
FinaleRevealCreamWashFx; melee / perfect-dodge wash twins) under this
edge. Oswald trust wash, victory wash, and finale-reveal wash also own
a delayed cream aftershock (flecks + soft halo; trust wash aftershock /
finale #176 / victory #168 / entry / purity-complete #132/#136 twin).
Punchline Act 2 tip hose (#91) and Silly Act 3 tip hose (#95) arm their
own tip washes (PunchlineTipCreamWashFx / SillyTipCreamWashFx) without
this edge. Mirrors reclaim wave-announce cream edge (#87) — sunny
Toontown cream only, opposite of the polluted ink edge vignette —
except trust-fracture cool cream / shadow-fade flecks (mid-act unease,
no twist spoilers). Campaign-owned; no keyblades / KH branding. Oswald
stays trusted mid-campaign (no twist spoilers on early trust cream edge
/ wash / wash aftershock). Victory cream edge + wash + aftershock clear
before the Oswald twist; finale-reveal cream edge + wash + wash
aftershock frame residual cream aftershock (#86) only.
"""

from math import cos, pi, sin

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

# CampaignGlobals prefix → defaults for fleck origin / node name.
_CFG_ACT = 'PLAY_ENTRY_BANNER_CREAM_EDGE'
_CFG_TRUST = 'OSWALD_TRUST_BANNER_CREAM_EDGE'
_CFG_TRUST_FRACTURE = 'OSWALD_TRUST_FRACTURE_CREAM_EDGE'
_CFG_HANDOFF = 'HANDOFF_CREAM_EDGE'
_CFG_VICTORY = 'VICTORY_CREAM_EDGE'
_CFG_FINALE_REVEAL = 'FINALE_REVEAL_CREAM_EDGE'
_DEFAULT_ORIGIN_ACT = (0.0, 0.0, 0.72)
_DEFAULT_ORIGIN_TRUST = (0.0, 0.0, 0.42)
_DEFAULT_ORIGIN_TRUST_FRACTURE = (0.0, 0.0, 0.42)
_DEFAULT_ORIGIN_HANDOFF = (0.0, 0.0, 0.40)
_DEFAULT_ORIGIN_VICTORY = (0.0, 0.0, 0.36)
_DEFAULT_ORIGIN_FINALE_REVEAL = (0.0, 0.0, 0.10)

_TAG_BY_CFG = {
    _CFG_ACT: 'act-banner',
    _CFG_TRUST: 'oswald-trust',
    _CFG_TRUST_FRACTURE: 'oswald-trust-fracture',
    _CFG_HANDOFF: 'handoff',
    _CFG_VICTORY: 'victory',
    _CFG_FINALE_REVEAL: 'finale-reveal',
}
_IVAL_BY_CFG = {
    _CFG_ACT: 'actBanner',
    _CFG_TRUST: 'oswaldTrust',
    _CFG_TRUST_FRACTURE: 'oswaldTrustFracture',
    _CFG_HANDOFF: 'handoff',
    _CFG_VICTORY: 'victory',
    _CFG_FINALE_REVEAL: 'finaleReveal',
}
# Paths that also rise cream-sparkle flecks along the cream frame.
_SPARKLE_CFGS = (_CFG_HANDOFF, _CFG_VICTORY, _CFG_FINALE_REVEAL)


class ActBannerCreamEdgeFx(object):
    """One-shot cream edge pulse framing a campaign banner."""

    def __init__(self, cfgPrefix=_CFG_ACT):
        self._cfgPrefix = cfgPrefix
        self._edgeIval = None
        self._edgeRootNP = None
        self._edgeFleckNPs = []
        self._edgeSparkleNPs = []

    def _cfg(self, suffix, default):
        return getattr(CampaignGlobals, '%s_%s' % (self._cfgPrefix, suffix),
                       default)

    def _tag(self):
        return _TAG_BY_CFG.get(self._cfgPrefix, 'act-banner')

    def _defaultOrigin(self):
        if self._cfgPrefix == _CFG_FINALE_REVEAL:
            return _DEFAULT_ORIGIN_FINALE_REVEAL
        if self._cfgPrefix == _CFG_VICTORY:
            return _DEFAULT_ORIGIN_VICTORY
        if self._cfgPrefix == _CFG_HANDOFF:
            return _DEFAULT_ORIGIN_HANDOFF
        if self._cfgPrefix == _CFG_TRUST_FRACTURE:
            return _DEFAULT_ORIGIN_TRUST_FRACTURE
        if self._cfgPrefix == _CFG_TRUST:
            return _DEFAULT_ORIGIN_TRUST
        return getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_POS', _DEFAULT_ORIGIN_ACT)

    def play(self):
        """Cream border strips + tip flecks framing the banner."""
        if not self._cfg('ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        edgeRoot = self._buildEdgeRoot(parent)
        if edgeRoot is None:
            return

        peak = float(self._cfg('PEAK', 0.42))
        mid = float(self._cfg('PULSE', 0.28))
        inSec = float(self._cfg('IN_SEC', 0.08))
        holdSec = float(self._cfg('HOLD_SEC', 0.10))
        pulseSec = float(self._cfg('PULSE_SEC', 0.12))
        outSec = float(self._cfg('OUT_SEC', 0.36))

        # Rubber-hose two-beat: bright pop → soft settle pulse → fade.
        edgePart = Sequence(
            LerpColorScaleInterval(
                edgeRoot, max(0.01, inSec), Vec4(1, 1, 1, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                edgeRoot, max(0.01, pulseSec), Vec4(1, 1, 1, mid),
                blendType='easeInOut'),
            LerpColorScaleInterval(
                edgeRoot, max(0.01, outSec), Vec4(1, 1, 1, 0),
                blendType='easeIn'),
        )
        fleckParts = self._spawnEdgeFlecks(parent)
        parts = [edgePart]
        parts.extend(fleckParts)
        # Handoff / victory cream-sparkle banners also rise cream glitter.
        if self._cfgPrefix in _SPARKLE_CFGS:
            parts.extend(self._spawnEdgeSparkles(parent))
        tag = _IVAL_BY_CFG.get(self._cfgPrefix, 'actBanner')
        self._edgeIval = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='%sCreamEdgePulse' % tag,
        )
        self._edgeIval.start()

    def _buildEdgeRoot(self, parent):
        """Four cream edge strips — sunny frame, open center for the banner."""
        try:
            # Thickness lives on the bare prefix (no _THICKNESS suffix) to
            # match PLAY_ENTRY_BANNER_CREAM_EDGE / OSWALD_TRUST_… /
            # HANDOFF_CREAM_EDGE / VICTORY_CREAM_EDGE /
            # FINALE_REVEAL_CREAM_EDGE.
            edge = float(getattr(
                CampaignGlobals, self._cfgPrefix, 0.28))
            binSort = int(self._cfg('BIN', 50))
            r, g, b, _a = self._cfg(
                'COLOR', (1.0, 0.97, 0.82, 1.0))
            tag = self._tag()
            root = parent.attachNewNode('%s-cream-edge' % tag)
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', binSort)
            root.setDepthTest(False)
            root.setDepthWrite(False)
            # Top / bottom / left / right — cream borders, clear middle.
            frames = (
                (-2.0, 2.0, 1.0 - edge, 1.25),
                (-2.0, 2.0, -1.25, -1.0 + edge),
                (-2.0, -1.0 + edge, -1.25, 1.25),
                (1.0 - edge, 2.0, -1.25, 1.25),
            )
            for i, frame in enumerate(frames):
                cm = CardMaker('%s-cream-edge-%s' % (tag, i))
                cm.setFrame(*frame)
                strip = root.attachNewNode(cm.generate())
                strip.setTransparency(TransparencyAttrib.MAlpha)
                strip.setColor(r, g, b, 1)
                strip.setBin('fixed', binSort)
                strip.setDepthTest(False)
                strip.setDepthWrite(False)
            self._edgeRootNP = root
            return root
        except Exception:
            self._edgeRootNP = None
            return None

    def _spawnEdgeFlecks(self, parent):
        """Sunny cream chips near the banner during the edge pulse."""
        count = int(self._cfg('FLECK_COUNT', 6))
        if count <= 0:
            return []
        size = float(self._cfg('FLECK_SIZE', 0.022))
        drift = float(self._cfg('FLECK_DRIFT', 0.18))
        sec = float(self._cfg('FLECK_SEC', 0.28))
        binSort = int(self._cfg('BIN', 50)) + 1
        r, g, b, a = self._cfg(
            'FLECK_COLOR', (1.0, 0.96, 0.62, 0.9))
        er, eg, eb, ea = self._cfg(
            'FLECK_END_COLOR', (1.0, 0.92, 0.45, 0.0))
        defaultOrigin = self._defaultOrigin()
        origin = self._cfg('FLECK_ORIGIN', defaultOrigin)
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = defaultOrigin

        tag = self._tag()
        parts = []
        for i in range(count):
            try:
                # Spread along the top banner band (not a full radial burst).
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (0.35 * pi) + (t * 0.9 * pi)
                cm = CardMaker('%s-cream-edge-fleck-%s' % (tag, i))
                if (i % 2) == 0:
                    cm.setFrame(
                        -size * 1.15, size * 1.15, -size * 0.5, size * 0.5)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                start = Point3(
                    ox + t * 0.55,
                    oy,
                    oz + 0.02 * (i % 3))
                fleck.setPos(start)
                fleck.setScale(0.4 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort)
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._edgeFleckNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                ox + cos(angle) * drift * 0.55 + t * 0.75,
                oy,
                oz + abs(sin(angle)) * drift + 0.04)
            delay = 0.02 * i
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                    LerpScaleInterval(fleck, 0.05, 1.0, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.1, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def _spawnEdgeSparkles(self, parent):
        """Cream-sparkle flecks rising along a cream-sparkle cream edge frame.

        Wave-edge #113 twin — handoff uses carnival cream-sparkle warmth
        (#99); victory uses victory cream-sparkle warmth (#105); finale
        reveal uses quieter residual aftershock glitter (#86). Chip/cross
        glitter along the top strip while confetti / swell / aftershock pops.
        """
        if not self._cfg('SPARKLE_ENABLED', True):
            return []
        count = int(self._cfg('SPARKLE_COUNT', 8))
        if count <= 0:
            return []
        size = float(self._cfg('SPARKLE_SIZE', 0.016))
        rise = float(self._cfg('SPARKLE_RISE', 0.28))
        spread = float(self._cfg('SPARKLE_SPREAD', 1.05))
        sec = float(self._cfg('SPARKLE_SEC', 0.40))
        binSort = int(self._cfg('BIN', 55)) + 2
        r, g, b, a = self._cfg(
            'SPARKLE_COLOR', (1.0, 0.97, 0.78, 0.90))
        er, eg, eb, ea = self._cfg(
            'SPARKLE_END_COLOR', (1.0, 0.94, 0.58, 0.0))
        if self._cfgPrefix == _CFG_FINALE_REVEAL:
            defaultOrigin = getattr(
                CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_ORIGIN',
                _DEFAULT_ORIGIN_FINALE_REVEAL)
        elif self._cfgPrefix == _CFG_VICTORY:
            defaultOrigin = getattr(
                CampaignGlobals, 'VICTORY_CREAM_SWELL_ORIGIN',
                _DEFAULT_ORIGIN_VICTORY)
        else:
            defaultOrigin = getattr(
                CampaignGlobals, 'HANDOFF_CONFETTI_ORIGIN',
                _DEFAULT_ORIGIN_HANDOFF)
        origin = self._cfg('SPARKLE_ORIGIN', defaultOrigin)
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = defaultOrigin

        tag = self._tag()
        parts = []
        for i in range(count):
            try:
                # Fan across the top cream strip; chip/cross like cream glitter.
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.28
                cm = CardMaker('%s-cream-edge-sparkle-%s' % (tag, i))
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.30, size * 1.30)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.30, size * 1.30, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                sparkle = parent.attachNewNode(cm.generate())
                sparkle.setTransparency(TransparencyAttrib.MAlpha)
                sparkle.setColor(r, g, b, 1)
                sparkle.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.03
                startZ = oz + 0.016 * (i % 3) + sin(angle) * 0.016
                sparkle.setPos(startX, oy, startZ)
                sparkle.setScale(0.4 + 0.08 * (i % 3))
                sparkle.setBin('fixed', binSort + (i % 2))
                sparkle.setDepthTest(False)
                sparkle.setDepthWrite(False)
                self._edgeSparkleNPs.append(sparkle)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.08,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            delay = 0.018 * i
            twinkle = 0.04 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        sparkle, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        sparkle, twinkle, 1.12, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        sparkle, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        sparkle, max(0.01, sec), 0.06, blendType='easeIn'),
                    LerpColorScaleInterval(
                        sparkle, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def clear(self):
        if self._edgeIval is not None:
            try:
                self._edgeIval.pause()
            except Exception:
                pass
            self._edgeIval = None
        root = self._edgeRootNP
        self._edgeRootNP = None
        if root is not None:
            try:
                if not root.isEmpty():
                    root.removeNode()
            except Exception:
                pass
        for np in self._edgeFleckNPs:
            if np is not None:
                try:
                    if not np.isEmpty():
                        np.removeNode()
                except Exception:
                    pass
        self._edgeFleckNPs = []
        for np in self._edgeSparkleNPs:
            if np is not None:
                try:
                    if not np.isEmpty():
                        np.removeNode()
                except Exception:
                    pass
        self._edgeSparkleNPs = []


_actFx = None
_trustFx = None
_trustFractureFx = None
_handoffFx = None
_victoryFx = None
_finaleRevealFx = None


def _sharedAct():
    global _actFx
    if _actFx is None:
        _actFx = ActBannerCreamEdgeFx(cfgPrefix=_CFG_ACT)
    return _actFx


def _sharedTrust():
    global _trustFx
    if _trustFx is None:
        _trustFx = ActBannerCreamEdgeFx(cfgPrefix=_CFG_TRUST)
    return _trustFx


def _sharedTrustFracture():
    global _trustFractureFx
    if _trustFractureFx is None:
        _trustFractureFx = ActBannerCreamEdgeFx(cfgPrefix=_CFG_TRUST_FRACTURE)
    return _trustFractureFx


def _sharedHandoff():
    global _handoffFx
    if _handoffFx is None:
        _handoffFx = ActBannerCreamEdgeFx(cfgPrefix=_CFG_HANDOFF)
    return _handoffFx


def _sharedVictory():
    global _victoryFx
    if _victoryFx is None:
        _victoryFx = ActBannerCreamEdgeFx(cfgPrefix=_CFG_VICTORY)
    return _victoryFx


def _sharedFinaleReveal():
    global _finaleRevealFx
    if _finaleRevealFx is None:
        _finaleRevealFx = ActBannerCreamEdgeFx(cfgPrefix=_CFG_FINALE_REVEAL)
    return _finaleRevealFx


def playActBannerCreamEdge():
    """Fire the shared act-banner cream edge pulse."""
    _sharedAct().play()


def clearActBannerCreamEdge():
    """Tear down any in-flight act-banner cream edge pulse."""
    if _actFx is not None:
        _actFx.clear()


def playOswaldTrustBannerCreamEdge():
    """Fire cream edge on early/mid Oswald trust handoff hose settle."""
    _sharedTrust().play()


def clearOswaldTrustBannerCreamEdge():
    """Tear down any in-flight Oswald trust cream edge pulse."""
    if _trustFx is not None:
        _trustFx.clear()


def playOswaldTrustFractureCreamEdge():
    """Fire cool cream → shadow fleck edge on mid-act trust fracture."""
    _sharedTrustFracture().play()


def clearOswaldTrustFractureCreamEdge():
    """Tear down any in-flight Oswald trust-fracture cream edge pulse."""
    if _trustFractureFx is not None:
        _trustFractureFx.clear()


def playHandoffCreamEdge():
    """Fire cream edge on hood handoff cream-sparkle carnival banners."""
    _sharedHandoff().play()


def clearHandoffCreamEdge():
    """Tear down any in-flight handoff cream-sparkle cream edge pulse."""
    if _handoffFx is not None:
        _handoffFx.clear()


def playVictoryCreamEdge():
    """Fire cream edge on victory cream confetti / sparkle banners."""
    _sharedVictory().play()


def clearVictoryCreamEdge():
    """Tear down any in-flight victory cream edge pulse."""
    if _victoryFx is not None:
        _victoryFx.clear()


def playFinaleRevealCreamEdge():
    """Fire cream edge on finale reveal cream aftershock banners."""
    _sharedFinaleReveal().play()


def clearFinaleRevealCreamEdge():
    """Tear down any in-flight finale-reveal cream edge pulse."""
    if _finaleRevealFx is not None:
        _finaleRevealFx.clear()

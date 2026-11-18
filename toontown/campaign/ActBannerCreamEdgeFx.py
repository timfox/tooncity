"""Rubber-hose cream edge pulse for campaign act-enter banners.

Soft cream border strips + tip flecks that frame PlayEntry act flash
banners (#70 hose pop). Mirrors reclaim wave-announce cream edge (#87) —
sunny Toontown cream only, opposite of the polluted ink edge vignette.
Campaign-owned; no keyblades / KH branding.
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


class ActBannerCreamEdgeFx(object):
    """One-shot cream edge pulse framing the act-enter banner."""

    def __init__(self):
        self._edgeIval = None
        self._edgeRootNP = None
        self._edgeFleckNPs = []

    def play(self):
        """Cream border strips + tip flecks framing the act banner."""
        if not getattr(
                CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        edgeRoot = self._buildEdgeRoot(parent)
        if edgeRoot is None:
            return

        peak = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_PEAK', 0.42))
        mid = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_PULSE', 0.28))
        inSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_IN_SEC', 0.08))
        holdSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_HOLD_SEC', 0.10))
        pulseSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_PULSE_SEC', 0.12))
        outSec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_OUT_SEC', 0.36))

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
        self._edgeIval = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='actBannerCreamEdgePulse',
        )
        self._edgeIval.start()

    def _buildEdgeRoot(self, parent):
        """Four cream edge strips — sunny frame, open center for the banner."""
        try:
            edge = float(getattr(
                CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE', 0.28))
            binSort = int(getattr(
                CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_BIN', 50))
            r, g, b, _a = getattr(
                CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_COLOR',
                (1.0, 0.97, 0.82, 1.0))
            root = parent.attachNewNode('act-banner-cream-edge')
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
                cm = CardMaker('act-banner-cream-edge-%s' % i)
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
        """Sunny cream chips near the act banner during the edge pulse."""
        count = int(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_COUNT', 6))
        if count <= 0:
            return []
        size = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_SIZE', 0.022))
        drift = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_DRIFT', 0.18))
        sec = float(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_SEC', 0.28))
        binSort = int(getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_BIN', 50)) + 1
        r, g, b, a = getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_COLOR',
            (1.0, 0.96, 0.62, 0.9))
        er, eg, eb, ea = getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_END_COLOR',
            (1.0, 0.92, 0.45, 0.0))
        origin = getattr(
            CampaignGlobals, 'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_ORIGIN',
            getattr(CampaignGlobals, 'PLAY_ENTRY_BANNER_POS',
                    (0.0, 0.0, 0.72)))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.72

        parts = []
        for i in range(count):
            try:
                # Spread along the top banner band (not a full radial burst).
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (0.35 * pi) + (t * 0.9 * pi)
                cm = CardMaker('act-banner-cream-edge-fleck-%s' % i)
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


_fx = None


def _shared():
    global _fx
    if _fx is None:
        _fx = ActBannerCreamEdgeFx()
    return _fx


def playActBannerCreamEdge():
    """Fire the shared act-banner cream edge pulse."""
    _shared().play()


def clearActBannerCreamEdge():
    """Tear down any in-flight cream edge pulse."""
    if _fx is not None:
        _fx.clear()

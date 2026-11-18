"""Neighborhood-hub placemarkers for polluted reclaim streets.

World-space tip / signpost breadcrumbs on Toontown Central playground
tunnels that lead to Loopy Lane, Punchline Place, and Silly Street.
Players notice ink-stained streets from the hub without magic words.

After the appear hose-pop, placemarkers briefly pulse / cream-highlight
so explore → fight reclaim tunnels read clearer on the sunny TTC hub.

Reads PollutionManager + reclaim/campaign street tables (import only);
does not rewrite those packages. Rubber-hose Toontown voice — no KH.
"""

from __future__ import annotations

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode, Vec4

from toontown.toonbase import ToontownGlobals

notify = directNotify.newCategory('CorruptStreetBreadcrumb')

# Hub playground only — TTC is the explore → fight → reclaim launchpad.
_HUB_ZONE = ToontownGlobals.ToontownCentral

# Placemarker float above tunnel mouth (world units).
_MARKER_Z = 4.5
_MARKER_SCALE = 1.35
# Soft rubber-hose pop when a polluted tunnel sign appears.
_POP_SQUASH = 0.72
_POP_STRETCH = 1.18
_POP_SETTLE_SEC = 0.28
# Brief attention pulse / cream highlight so reclaim tunnels read on the hub.
_PULSE_PEAK = 1.22
_PULSE_HALF_SEC = 0.16
_PULSE_BEATS = 2
_PULSE_GAP_SEC = 4.8
_PULSE_HIGHLIGHT = Vec4(1.0, 0.88, 0.58, 1.0)
_PULSE_REST = Vec4(1.0, 1.0, 1.0, 1.0)

# Short rubber-hose signpost copy (world placemarker — keep punchy).
_STREET_COPY = {
    ToontownGlobals.LoopyLane: 'Ink stains Loopy — hop in & reclaim!',
    ToontownGlobals.PunchlinePlace: 'Sludge jokes on Punchline — reclaim!',
    ToontownGlobals.SillyStreet: 'Silly Street ink-deep — reclaim with Oswald!',
}

# Ink-on-cream placemarker colors (readable against sunny TTC tunnels).
_TEXT_FG = Vec4(0.18, 0.12, 0.22, 1.0)
_TEXT_SHADOW = Vec4(1.0, 0.94, 0.78, 0.92)


def reclaimStreetEntries():
    """[(zoneId, streetName, placemarkerText, seedPollution), ...] for hub tips.

    Prefers CampaignGlobals.ACTS, falls back to ReclaimGlobals.STREET_PACKS.
    Pure helper — safe for AST / headless import checks without Panda geom.
    """
    entries = []
    seen = set()
    try:
        from toontown.campaign import CampaignGlobals
        for act in getattr(CampaignGlobals, 'ACTS', ()) or ():
            zoneId = int(act.get('zoneId', 0) or 0)
            if zoneId <= 0 or zoneId in seen:
                continue
            name = act.get('name') or ('Street %s' % zoneId)
            seed = float(act.get('seedPollution', 0.0) or 0.0)
            text = _STREET_COPY.get(zoneId) or (
                'Corruption stains %s — hop the tunnel & reclaim!' % name)
            entries.append((zoneId, name, text, seed))
            seen.add(zoneId)
    except Exception:
        pass
    if entries:
        return entries
    try:
        from toontown.reclaim import ReclaimGlobals
        packs = getattr(ReclaimGlobals, 'STREET_PACKS', {}) or {}
        for zoneId, pack in packs.items():
            zoneId = int(zoneId)
            if zoneId in seen:
                continue
            name = (pack or {}).get('name') or ('Street %s' % zoneId)
            seed = float((pack or {}).get('seedPollution', 0.0) or 0.0)
            text = _STREET_COPY.get(zoneId) or (
                'Corruption stains %s — hop the tunnel & reclaim!' % name)
            entries.append((zoneId, name, text, seed))
            seen.add(zoneId)
    except Exception:
        pass
    return entries


def streetNeedsBreadcrumb(zoneId, pollutionByZone, seedPollution, pure=0.0):
    """True when a reclaim street still looks polluted from the hub.

    Known PollutionManager samples win; unknown zones fall back to seed
    pollution so Loopy / Punchline / Silly stay discoverable before visit.
    """
    zoneId = int(zoneId)
    pure = float(pure)
    if zoneId in pollutionByZone:
        try:
            return float(pollutionByZone[zoneId]) > pure
        except (TypeError, ValueError):
            return False
    try:
        return float(seedPollution) > pure
    except (TypeError, ValueError):
        return False


def placemarkerPulseParams():
    """Pure timing / scale for hub tunnel placemarker notice pulse.

    Headless-safe — no Panda geom. Used by AST / unit checks for the
    explore → fight attention cue on polluted reclaim tunnels.
    """
    return {
        'peak': float(_PULSE_PEAK),
        'halfSec': float(_PULSE_HALF_SEC),
        'beats': int(_PULSE_BEATS),
        'gapSec': float(_PULSE_GAP_SEC),
        'baseScale': float(_MARKER_SCALE),
    }


def _pollutionPure():
    try:
        from toontown.corruption import CorruptionGlobals
        return float(getattr(CorruptionGlobals, 'POLLUTION_PURE', 0.0))
    except Exception:
        return 0.0


class CorruptStreetBreadcrumb(DirectObject):
    """Attach / refresh polluted-street placemarkers on hub playground tunnels."""

    notify = notify

    def __init__(self, playground):
        DirectObject.__init__(self)
        self._playground = playground
        self._markers = {}  # zoneId -> NodePath
        self._popIvals = {}
        self._pulseIvals = {}
        self._active = False

    def start(self):
        if self._active:
            return
        self._active = True
        self.accept('pollutionChanged', self._onPollutionChanged)
        self.accept('purityRestoreFx', self._onPurityRestore)
        self.accept('exitPlayground', self.stop)
        self._requestStreetPollution()
        self.refresh()

    def stop(self):
        if not self._active and not self._markers:
            return
        self._active = False
        self.ignore('pollutionChanged')
        self.ignore('purityRestoreFx')
        self.ignore('exitPlayground')
        self._clearMarkers()

    def destroy(self):
        self.stop()
        self.ignoreAll()
        self._playground = None

    def _requestStreetPollution(self):
        """Ask PollutionManager for Loopy / Punchline / Silly samples."""
        pm = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if pm is None or not hasattr(pm, 'd_requestZonePollution'):
            return
        for zoneId, _name, _text, _seed in reclaimStreetEntries():
            try:
                pm.d_requestZonePollution(int(zoneId))
            except Exception:
                self.notify.debug('pollution request failed for %s' % zoneId)

    def _pollutionMap(self):
        pm = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return {}
        return dict(getattr(pm, 'zonePollution', {}) or {})

    def _onPollutionChanged(self, zoneId=None, level=None):
        if not self._active:
            return
        # Only refresh when a reclaim street (or unknown) updates.
        reclaimZones = {z for z, _n, _t, _s in reclaimStreetEntries()}
        if zoneId is not None and int(zoneId) not in reclaimZones:
            return
        self.refresh()

    def _onPurityRestore(self, *args):
        if self._active:
            self.refresh()

    def refresh(self):
        if not self._active:
            return
        playground = self._playground
        if playground is None:
            return
        hoodId = getattr(getattr(playground, 'loader', None), 'hood', None)
        hoodId = getattr(hoodId, 'id', None)
        if hoodId is not None and int(hoodId) != int(_HUB_ZONE):
            self._clearMarkers()
            return
        pollution = self._pollutionMap()
        pure = _pollutionPure()
        wanted = {}
        for zoneId, name, text, seed in reclaimStreetEntries():
            if streetNeedsBreadcrumb(zoneId, pollution, seed, pure=pure):
                wanted[int(zoneId)] = (name, text)
        # Drop cleared streets.
        for zoneId in list(self._markers.keys()):
            if zoneId not in wanted:
                self._removeMarker(zoneId)
        # Ensure placemarkers for still-polluted reclaim tunnels.
        for zoneId, (name, text) in wanted.items():
            if zoneId not in self._markers:
                self._attachMarker(zoneId, name, text)

    def _findLinkTunnel(self, zoneId):
        playground = self._playground
        if playground is None:
            return None
        nodeList = getattr(getattr(playground, 'loader', None), 'nodeList', None)
        if not nodeList:
            return None
        # linktunnel_<hood>_<zone> — HoodMgr parses parts[1]/parts[2].
        zoneId = int(zoneId)
        for root in nodeList:
            try:
                matches = root.findAllMatches('**/linktunnel*')
            except Exception:
                continue
            for i in range(matches.getNumPaths()):
                link = matches.getPath(i)
                parts = (link.getName() or '').split('_')
                if len(parts) < 3:
                    continue
                try:
                    if int(parts[2]) == zoneId:
                        return link
                except ValueError:
                    continue
        return None

    def _attachMarker(self, zoneId, streetName, text):
        link = self._findLinkTunnel(zoneId)
        if link is None or link.isEmpty():
            self.notify.debug(
                'no linktunnel for polluted street %s (%s)' % (zoneId, streetName))
            return
        # Avoid stacking if DNA already has a leftover marker name.
        existing = link.find('**/corruptStreetBreadcrumb')
        if not existing.isEmpty():
            existing.removeNode()
        tn = TextNode('corruptStreetBreadcrumbText')
        try:
            tn.setFont(ToontownGlobals.getSignFont())
        except Exception:
            pass
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(_TEXT_FG)
        try:
            tn.setShadow(0.04, 0.04)
            tn.setShadowColor(_TEXT_SHADOW)
        except Exception:
            pass
        np = link.attachNewNode(tn)
        np.setName('corruptStreetBreadcrumb')
        np.setPos(0, 0, _MARKER_Z)
        np.setScale(_MARKER_SCALE)
        np.setBillboardPointEye()
        np.setDepthWrite(0)
        np.setBin('fixed', 40)
        self._markers[int(zoneId)] = np
        self._playPop(zoneId, np)
        self.notify.debug(
            'placemarker on tunnel → %s (%s)' % (streetName, zoneId))

    def _playPop(self, zoneId, np):
        self._stopPulse(zoneId)
        old = self._popIvals.pop(zoneId, None)
        if old is not None:
            try:
                old.finish()
            except Exception:
                pass
        baseScale = _MARKER_SCALE
        ival = Sequence(
            LerpScaleInterval(
                np, _POP_SETTLE_SEC * 0.35,
                baseScale * _POP_SQUASH,
                startScale=baseScale * 0.05),
            LerpScaleInterval(
                np, _POP_SETTLE_SEC * 0.35,
                baseScale * _POP_STRETCH,
                startScale=baseScale * _POP_SQUASH),
            LerpScaleInterval(
                np, _POP_SETTLE_SEC * 0.30,
                baseScale,
                startScale=baseScale * _POP_STRETCH),
            # Brief cream/scale pulse so reclaim tunnels catch the eye.
            Func(self._startPulseLoop, zoneId, np),
        )
        self._popIvals[zoneId] = ival
        try:
            ival.start()
        except Exception:
            np.setScale(baseScale)
            self._startPulseLoop(zoneId, np)

    def _buildNoticePulseIval(self, np):
        """One brief rubber-hose scale + cream highlight pulse."""
        baseScale = _MARKER_SCALE
        half = max(0.01, float(_PULSE_HALF_SEC))
        peak = baseScale * float(_PULSE_PEAK)
        restCs = _PULSE_REST
        hiCs = _PULSE_HIGHLIGHT
        beats = []
        for _ in range(max(1, int(_PULSE_BEATS))):
            beats.append(Parallel(
                Sequence(
                    LerpScaleInterval(
                        np, half, peak, startScale=baseScale,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        np, half, baseScale, startScale=peak,
                        blendType='easeIn'),
                ),
                Sequence(
                    LerpColorScaleInterval(
                        np, half, hiCs, startColorScale=restCs,
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        np, half, restCs, startColorScale=hiCs,
                        blendType='easeIn'),
                ),
            ))
        return Sequence(*beats)

    def _startPulseLoop(self, zoneId, np):
        """Sparse brief pulses while the polluted placemarker stays up."""
        zoneId = int(zoneId)
        if not self._active or self._markers.get(zoneId) is not np:
            return
        if np is None:
            return
        try:
            if np.isEmpty():
                return
        except Exception:
            return
        self._stopPulse(zoneId)
        try:
            np.setColorScale(_PULSE_REST)
            np.setScale(_MARKER_SCALE)
        except Exception:
            pass
        gap = max(0.5, float(_PULSE_GAP_SEC))
        loop = Sequence(
            self._buildNoticePulseIval(np),
            Wait(gap),
        )
        self._pulseIvals[zoneId] = loop
        try:
            loop.loop()
        except Exception:
            self._pulseIvals.pop(zoneId, None)
            try:
                np.setScale(_MARKER_SCALE)
                np.setColorScale(_PULSE_REST)
            except Exception:
                pass

    def _stopPulse(self, zoneId):
        zoneId = int(zoneId)
        ival = self._pulseIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                try:
                    ival.pause()
                except Exception:
                    pass

    def _removeMarker(self, zoneId):
        zoneId = int(zoneId)
        self._stopPulse(zoneId)
        ival = self._popIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                pass
        np = self._markers.pop(zoneId, None)
        if np is not None:
            try:
                np.removeNode()
            except Exception:
                pass

    def _clearMarkers(self):
        for zoneId in list(self._markers.keys()):
            self._removeMarker(zoneId)


_activeBreadcrumb = None


def ensureCorruptStreetBreadcrumbs(playground):
    """Start (or refresh) hub tunnel placemarkers for the given playground."""
    global _activeBreadcrumb
    if playground is None:
        return None
    if _activeBreadcrumb is not None:
        try:
            _activeBreadcrumb.destroy()
        except Exception:
            pass
        _activeBreadcrumb = None
    crumb = CorruptStreetBreadcrumb(playground)
    crumb.start()
    _activeBreadcrumb = crumb
    return crumb


def stopCorruptStreetBreadcrumbs():
    global _activeBreadcrumb
    if _activeBreadcrumb is not None:
        try:
            _activeBreadcrumb.destroy()
        except Exception:
            pass
        _activeBreadcrumb = None

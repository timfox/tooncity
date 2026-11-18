"""Neighborhood-hub placemarkers for polluted reclaim streets.

World-space tip / signpost breadcrumbs on Toontown Central playground
tunnels that lead to Loopy Lane, Punchline Place, and Silly Street.
Players notice ink-stained streets from the hub without magic words.

After the appear hose-pop, placemarkers briefly pulse / cream-highlight
(#211), deepened with a juicier cream mid-settle + soft local cream
halo so discoverability reads punchier without KH branding — distinct
from the birds-return fullscreen cream wash (#226). Separately, a short
ink crumb trail at the tunnel mouth pulses on a faster stagger so
polluted streets read clearer from the playground side without relying
on the overhead placemarker alone. A soft pollution fog edge veil also
breathes at the playground-side tunnel lip so corruption presence reads
before you enter a reclaim street — distinct from both placemarker
(#211) and crumb (#216) scale pulses.

When a polluted reclaim tunnel clears (or purityRestoreFx fires while
the hub is live), a brief birds-return cream wash pulses so the
playground feeling clean reads juicily beside PollutionStreetAudio
pure-street birds (#55) — see BirdsReturnCreamWashFx.

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
from panda3d.core import CardMaker, TextNode, TransparencyAttrib, Vec4

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
# Cream deepen: warmer peak → soft mid settle + local cream halo bloom
# (not birds-return fullscreen wash #226; not crumb #216 / fog #221).
_PULSE_PEAK = 1.22
_PULSE_HALF_SEC = 0.16
_PULSE_BEATS = 2
_PULSE_GAP_SEC = 4.8
_PULSE_HIGHLIGHT = Vec4(1.0, 0.93, 0.52, 1.0)  # juicier sunny cream peak
_PULSE_CREAM_MID = Vec4(1.0, 0.96, 0.72, 1.0)  # soft settle before rest
_PULSE_CREAM_MID_SEC = 0.09
_PULSE_REST = Vec4(1.0, 1.0, 1.0, 1.0)
# Soft local cream halo behind placemarker during notice pulse.
_PULSE_HALO_NAME = 'corruptStreetPlacemarkerCreamHalo'
_PULSE_HALO_HALF_W = 2.55
_PULSE_HALO_HALF_H = 0.62
_PULSE_HALO_Z_OFF = -0.08
_PULSE_HALO_SCALE_PEAK = 1.32
_PULSE_HALO_PEAK = Vec4(1.0, 0.96, 0.78, 0.38)
_PULSE_HALO_MID = Vec4(1.0, 0.94, 0.70, 0.16)
_PULSE_HALO_REST = Vec4(1.0, 0.97, 0.82, 0.0)

# Tunnel-mouth ink crumb trail — distinct from overhead placemarker pulse.
_CRUMB_GLYPH = '•'
_CRUMB_COUNT = 3
_CRUMB_Z = 1.05
_CRUMB_Y0 = -2.4
_CRUMB_Y_STEP = 1.05
_CRUMB_SCALE = 0.55
_CRUMB_PULSE_PEAK = 1.38
_CRUMB_PULSE_HALF_SEC = 0.11
_CRUMB_PULSE_GAP_SEC = 3.1
_CRUMB_STAGGER_SEC = 0.13
_CRUMB_FG = Vec4(0.22, 0.10, 0.28, 0.95)
_CRUMB_SHADOW = Vec4(1.0, 0.92, 0.72, 0.75)
_CRUMB_HIGHLIGHT = Vec4(1.0, 0.84, 0.48, 1.0)
_CRUMB_REST = Vec4(1.0, 1.0, 1.0, 1.0)

# Playground-edge pollution fog breath — opacity/billow, not scale+cream.
# Slower / softer than placemarker (#211) and crumb (#216) so corruption
# presence reads at the tunnel lip before you hop a reclaim street.
_FOG_NAME = 'playgroundPollutionFogEdge'
_FOG_Y = -0.55
_FOG_Z = 0.42
_FOG_HALF_W = 3.2
_FOG_HALF_H = 0.95
_FOG_SCALE = 1.0
_FOG_BILLOW = 1.10
_FOG_PULSE_HALF_SEC = 0.44
_FOG_PULSE_GAP_SEC = 6.2
_FOG_REST = Vec4(0.16, 0.10, 0.20, 0.16)
_FOG_PEAK = Vec4(0.12, 0.06, 0.16, 0.36)

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


def placemarkerPulseCreamParams():
    """Pure cream-deepen params for hub tunnel placemarker notice pulse.

    Juicier cream mid-settle + local halo bloom on the #211 scale pulse.
    Distinct from BirdsReturnCreamWashFx fullscreen wash (#226) and from
    crumb (#216) / fog (#221) cues. Headless-safe — no Panda geom.
    """
    hi = _PULSE_HIGHLIGHT
    mid = _PULSE_CREAM_MID
    haloPeak = _PULSE_HALO_PEAK
    haloMid = _PULSE_HALO_MID
    return {
        'highlight': (float(hi[0]), float(hi[1]), float(hi[2]), float(hi[3])),
        'creamMid': (float(mid[0]), float(mid[1]), float(mid[2]), float(mid[3])),
        'creamMidSec': float(_PULSE_CREAM_MID_SEC),
        'haloPeakAlpha': float(haloPeak[3]),
        'haloMidAlpha': float(haloMid[3]),
        'haloScalePeak': float(_PULSE_HALO_SCALE_PEAK),
        'haloHalfW': float(_PULSE_HALO_HALF_W),
        'haloHalfH': float(_PULSE_HALO_HALF_H),
        # Not a fullscreen wash — local world-space placemarker halo only.
        'fullscreenWash': False,
    }


def streetBreadcrumbPulseParams():
    """Pure timing / scale for tunnel-mouth ink crumb trail pulse.

    Distinct from placemarkerPulseParams (#211): faster gap, single-beat
    stagger along the crumb trail so polluted streets read from the
    playground approach. Headless-safe — no Panda geom.
    """
    return {
        'peak': float(_CRUMB_PULSE_PEAK),
        'halfSec': float(_CRUMB_PULSE_HALF_SEC),
        'gapSec': float(_CRUMB_PULSE_GAP_SEC),
        'staggerSec': float(_CRUMB_STAGGER_SEC),
        'count': int(_CRUMB_COUNT),
        'baseScale': float(_CRUMB_SCALE),
    }


def playgroundFogEdgePulseParams():
    """Pure timing / alpha for playground pollution fog edge breath.

    Distinct from placemarkerPulseParams (#211) and
    streetBreadcrumbPulseParams (#216): slower gap, opacity+billow (no
    cream scale snap) so corruption presence reads at the tunnel lip
    before reclaim entry. Headless-safe — no Panda geom.
    """
    return {
        'halfSec': float(_FOG_PULSE_HALF_SEC),
        'gapSec': float(_FOG_PULSE_GAP_SEC),
        'restAlpha': float(_FOG_REST[3]),
        'peakAlpha': float(_FOG_PEAK[3]),
        'billow': float(_FOG_BILLOW),
        'baseScale': float(_FOG_SCALE),
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
        self._pulseHalos = {}  # zoneId -> NodePath (cream deepen halo)
        self._crumbTrails = {}  # zoneId -> [NodePath, ...]
        self._fogEdges = {}  # zoneId -> NodePath
        self._popIvals = {}
        self._pulseIvals = {}
        self._crumbPulseIvals = {}
        self._fogPulseIvals = {}
        self._lastPollutionLevels = {}  # zoneId -> last known level
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
        self._clearBirdsReturnCreamWash()

    def destroy(self):
        self.stop()
        self.ignoreAll()
        self._playground = None

    def _cueBirdsReturnCreamWash(self):
        """Soft cream wash when playground pollution clears / birds return."""
        try:
            from toontown.safezone.BirdsReturnCreamWashFx import (
                playBirdsReturnCreamWash)
            playBirdsReturnCreamWash()
        except Exception:
            self.notify.debug('birds return cream wash unavailable')

    def _clearBirdsReturnCreamWash(self):
        try:
            from toontown.safezone.BirdsReturnCreamWashFx import (
                clearBirdsReturnCreamWash)
            clearBirdsReturnCreamWash()
        except Exception:
            pass

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
        prevLevel = None
        if zoneId is not None:
            zid = int(zoneId)
            prevLevel = self._lastPollutionLevels.get(zid)
            if level is not None:
                try:
                    self._lastPollutionLevels[zid] = float(level)
                except (TypeError, ValueError):
                    pass
        hadMarker = (
            zoneId is not None and int(zoneId) in self._markers)
        self.refresh()
        # Pollution clear → cream wash beside pure-street birds return (#55).
        # Debounce lives in BirdsReturnCreamWashFx.
        clearedMarker = (
            hadMarker and zoneId is not None
            and int(zoneId) not in self._markers)
        flippedPure = False
        if prevLevel is not None and level is not None:
            try:
                from toontown.safezone.BirdsReturnCreamWashFx import (
                    shouldPlayBirdsReturnCreamWash)
                flippedPure = shouldPlayBirdsReturnCreamWash(
                    prevLevel, level)
            except Exception:
                flippedPure = False
        if clearedMarker or flippedPure:
            self._cueBirdsReturnCreamWash()

    def _onPurityRestore(self, *args):
        if not self._active:
            return
        hadAny = bool(self._markers)
        self.refresh()
        # Reclaim complete / purity restore while hub live — birds return cue.
        if hadAny or args:
            self._cueBirdsReturnCreamWash()

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
        # Drop cleared streets (caller may cue birds-return cream wash).
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
        halo = self._attachPulseCreamHalo(link, zoneId)
        crumbs = self._attachCrumbTrail(link, zoneId)
        fog = self._attachFogEdge(link, zoneId)
        self._playPop(zoneId, np, crumbs, fog, halo=halo)
        self.notify.debug(
            'placemarker on tunnel → %s (%s)' % (streetName, zoneId))

    def _attachPulseCreamHalo(self, link, zoneId):
        """Soft local cream halo behind placemarker — deepen #211 cream cue."""
        zoneId = int(zoneId)
        old = self._pulseHalos.pop(zoneId, None)
        if old is not None:
            try:
                old.removeNode()
            except Exception:
                pass
        leftover = link.find('**/%s' % _PULSE_HALO_NAME)
        if not leftover.isEmpty():
            leftover.removeNode()
        halo = None
        try:
            cm = CardMaker(_PULSE_HALO_NAME)
            cm.setFrame(
                -_PULSE_HALO_HALF_W, _PULSE_HALO_HALF_W,
                -_PULSE_HALO_HALF_H, _PULSE_HALO_HALF_H)
            halo = link.attachNewNode(cm.generate())
            halo.setName(_PULSE_HALO_NAME)
            halo.setTransparency(TransparencyAttrib.MAlpha)
            # Sit just behind the placemarker text (bin under fixed/40).
            halo.setPos(0, 0, _MARKER_Z + _PULSE_HALO_Z_OFF)
            halo.setScale(1.0)
            halo.setColorScale(_PULSE_HALO_REST)
            halo.setDepthWrite(0)
            halo.setBin('fixed', 38)  # under placemarker (40), over fog (37)
            halo.setBillboardPointEye()
        except Exception:
            self.notify.debug(
                'placemarker cream halo unavailable for zone %s' % zoneId)
            halo = None
        if halo is not None:
            self._pulseHalos[zoneId] = halo
        return halo

    def _attachFogEdge(self, link, zoneId):
        """Soft ink fog veil at the playground-side tunnel lip."""
        zoneId = int(zoneId)
        self._stopFogPulse(zoneId)
        old = self._fogEdges.pop(zoneId, None)
        if old is not None:
            try:
                old.removeNode()
            except Exception:
                pass
        leftover = link.find('**/%s' % _FOG_NAME)
        if not leftover.isEmpty():
            leftover.removeNode()
        fog = None
        try:
            cm = CardMaker(_FOG_NAME)
            cm.setFrame(-_FOG_HALF_W, _FOG_HALF_W, 0.0, _FOG_HALF_H * 2.0)
            fog = link.attachNewNode(cm.generate())
            fog.setName(_FOG_NAME)
            fog.setTransparency(TransparencyAttrib.MAlpha)
            fog.setPos(0, _FOG_Y, _FOG_Z)
            fog.setScale(_FOG_SCALE)
            fog.setColorScale(_FOG_REST)
            fog.setDepthWrite(0)
            fog.setBin('fixed', 37)  # under crumb (39) + placemarker (40)
            fog.setBillboardPointEye()
        except Exception:
            self.notify.debug('fog edge unavailable for zone %s' % zoneId)
            fog = None
        if fog is not None:
            self._fogEdges[zoneId] = fog
        return fog

    def _attachCrumbTrail(self, link, zoneId):
        """Ink crumb dots at the tunnel mouth — playground-side breadcrumb."""
        zoneId = int(zoneId)
        self._stopCrumbPulse(zoneId)
        oldTrail = self._crumbTrails.pop(zoneId, None)
        if oldTrail:
            for crumb in oldTrail:
                try:
                    crumb.removeNode()
                except Exception:
                    pass
        # Drop leftover DNA crumbs if a prior session left them.
        leftover = link.find('**/corruptStreetCrumbTrail')
        if not leftover.isEmpty():
            leftover.removeNode()
        root = link.attachNewNode('corruptStreetCrumbTrail')
        crumbs = []
        for i in range(max(1, int(_CRUMB_COUNT))):
            tn = TextNode('corruptStreetCrumbText-%s' % i)
            try:
                tn.setFont(ToontownGlobals.getSignFont())
            except Exception:
                pass
            tn.setText(_CRUMB_GLYPH)
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(_CRUMB_FG)
            try:
                tn.setShadow(0.03, 0.03)
                tn.setShadowColor(_CRUMB_SHADOW)
            except Exception:
                pass
            crumb = root.attachNewNode(tn)
            crumb.setName('corruptStreetCrumb')
            crumb.setPos(0, _CRUMB_Y0 + (i * _CRUMB_Y_STEP), _CRUMB_Z)
            crumb.setScale(_CRUMB_SCALE)
            crumb.setBillboardPointEye()
            crumb.setDepthWrite(0)
            crumb.setBin('fixed', 39)
            crumbs.append(crumb)
        self._crumbTrails[zoneId] = crumbs
        return crumbs

    def _playPop(self, zoneId, np, crumbs=None, fog=None, halo=None):
        self._stopPulse(zoneId)
        self._stopCrumbPulse(zoneId)
        self._stopFogPulse(zoneId)
        old = self._popIvals.pop(zoneId, None)
        if old is not None:
            try:
                old.finish()
            except Exception:
                pass
        if halo is None:
            halo = self._pulseHalos.get(int(zoneId))
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
            # Placemarker cream deepen (#211+) + crumb + fog-edge pulses.
            Func(self._startPulseLoop, zoneId, np, halo),
            Func(self._startCrumbPulseLoop, zoneId, crumbs or ()),
            Func(self._startFogPulseLoop, zoneId, fog),
        )
        self._popIvals[zoneId] = ival
        try:
            ival.start()
        except Exception:
            np.setScale(baseScale)
            self._startPulseLoop(zoneId, np, halo)
            self._startCrumbPulseLoop(zoneId, crumbs or ())
            self._startFogPulseLoop(zoneId, fog)

    def _buildNoticePulseIval(self, np, halo=None):
        """One brief rubber-hose scale + deepened cream highlight pulse."""
        baseScale = _MARKER_SCALE
        half = max(0.01, float(_PULSE_HALF_SEC))
        midSec = max(0.01, float(_PULSE_CREAM_MID_SEC))
        peak = baseScale * float(_PULSE_PEAK)
        restCs = _PULSE_REST
        hiCs = _PULSE_HIGHLIGHT
        midCs = _PULSE_CREAM_MID
        # Scale still snaps out/in; cream settles peak → mid → rest (juicier).
        scaleOut = half
        scaleIn = half + midSec
        beats = []
        for _ in range(max(1, int(_PULSE_BEATS))):
            parts = [
                Sequence(
                    LerpScaleInterval(
                        np, scaleOut, peak, startScale=baseScale,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        np, scaleIn, baseScale, startScale=peak,
                        blendType='easeIn'),
                ),
                Sequence(
                    LerpColorScaleInterval(
                        np, half, hiCs, startColorScale=restCs,
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        np, midSec, midCs, startColorScale=hiCs,
                        blendType='easeInOut'),
                    LerpColorScaleInterval(
                        np, half, restCs, startColorScale=midCs,
                        blendType='easeIn'),
                ),
            ]
            if halo is not None:
                parts.append(self._buildPulseCreamHaloIval(halo, half, midSec))
            beats.append(Parallel(*parts))
        return Sequence(*beats)

    def _buildPulseCreamHaloIval(self, halo, half, midSec):
        """Local cream halo bloom — peak → mid → fade (not fullscreen wash)."""
        peakScale = float(_PULSE_HALO_SCALE_PEAK)
        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    halo, half, _PULSE_HALO_PEAK,
                    startColorScale=_PULSE_HALO_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    halo, midSec, _PULSE_HALO_MID,
                    startColorScale=_PULSE_HALO_PEAK, blendType='easeInOut'),
                LerpColorScaleInterval(
                    halo, half, _PULSE_HALO_REST,
                    startColorScale=_PULSE_HALO_MID, blendType='easeIn'),
            ),
            Sequence(
                LerpScaleInterval(
                    halo, half, peakScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    halo, half + midSec, 1.0, startScale=peakScale,
                    blendType='easeIn'),
            ),
        )

    def _startPulseLoop(self, zoneId, np, halo=None):
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
        if halo is None:
            halo = self._pulseHalos.get(zoneId)
        self._stopPulse(zoneId)
        try:
            np.setColorScale(_PULSE_REST)
            np.setScale(_MARKER_SCALE)
        except Exception:
            pass
        if halo is not None:
            try:
                halo.setColorScale(_PULSE_HALO_REST)
                halo.setScale(1.0)
            except Exception:
                pass
        gap = max(0.5, float(_PULSE_GAP_SEC))
        loop = Sequence(
            self._buildNoticePulseIval(np, halo),
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
            if halo is not None:
                try:
                    halo.setColorScale(_PULSE_HALO_REST)
                    halo.setScale(1.0)
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
        halo = self._pulseHalos.get(zoneId)
        if halo is not None:
            try:
                halo.setColorScale(_PULSE_HALO_REST)
                halo.setScale(1.0)
            except Exception:
                pass

    def _buildCrumbPulseIval(self, crumb):
        """One brief scale + cream beat on a single trail crumb."""
        baseScale = _CRUMB_SCALE
        half = max(0.01, float(_CRUMB_PULSE_HALF_SEC))
        peak = baseScale * float(_CRUMB_PULSE_PEAK)
        return Parallel(
            Sequence(
                LerpScaleInterval(
                    crumb, half, peak, startScale=baseScale,
                    blendType='easeOut'),
                LerpScaleInterval(
                    crumb, half, baseScale, startScale=peak,
                    blendType='easeIn'),
            ),
            Sequence(
                LerpColorScaleInterval(
                    crumb, half, _CRUMB_HIGHLIGHT,
                    startColorScale=_CRUMB_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    crumb, half, _CRUMB_REST,
                    startColorScale=_CRUMB_HIGHLIGHT, blendType='easeIn'),
            ),
        )

    def _startCrumbPulseLoop(self, zoneId, crumbs=None):
        """Staggered crumb-trail pulse — faster / distinct from placemarker."""
        zoneId = int(zoneId)
        # Always pulse the live trail for this zone (Func may pass a snapshot).
        crumbs = self._crumbTrails.get(zoneId) or []
        if not self._active or not crumbs:
            return
        alive = []
        for crumb in crumbs:
            try:
                if crumb is not None and not crumb.isEmpty():
                    alive.append(crumb)
            except Exception:
                continue
        if not alive:
            return
        self._stopCrumbPulse(zoneId)
        for crumb in alive:
            try:
                crumb.setColorScale(_CRUMB_REST)
                crumb.setScale(_CRUMB_SCALE)
            except Exception:
                pass
        stagger = max(0.0, float(_CRUMB_STAGGER_SEC))
        gap = max(0.4, float(_CRUMB_PULSE_GAP_SEC))
        # Overlapping chase into the tunnel — not the overhead placemarker loop.
        parts = []
        for i, crumb in enumerate(alive):
            parts.append(Sequence(
                Wait(stagger * i),
                self._buildCrumbPulseIval(crumb),
            ))
        loop = Sequence(Parallel(*parts), Wait(gap))
        self._crumbPulseIvals[zoneId] = loop
        try:
            loop.loop()
        except Exception:
            self._crumbPulseIvals.pop(zoneId, None)
            for crumb in alive:
                try:
                    crumb.setScale(_CRUMB_SCALE)
                    crumb.setColorScale(_CRUMB_REST)
                except Exception:
                    pass

    def _stopCrumbPulse(self, zoneId):
        zoneId = int(zoneId)
        ival = self._crumbPulseIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                try:
                    ival.pause()
                except Exception:
                    pass

    def _buildFogPulseIval(self, fog):
        """One soft opacity + billow breath on the playground fog edge."""
        half = max(0.05, float(_FOG_PULSE_HALF_SEC))
        baseScale = float(_FOG_SCALE)
        peakScale = baseScale * float(_FOG_BILLOW)
        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    fog, half, _FOG_PEAK, startColorScale=_FOG_REST,
                    blendType='easeInOut'),
                LerpColorScaleInterval(
                    fog, half, _FOG_REST, startColorScale=_FOG_PEAK,
                    blendType='easeInOut'),
            ),
            Sequence(
                LerpScaleInterval(
                    fog, half, peakScale, startScale=baseScale,
                    blendType='easeInOut'),
                LerpScaleInterval(
                    fog, half, baseScale, startScale=peakScale,
                    blendType='easeInOut'),
            ),
        )

    def _startFogPulseLoop(self, zoneId, fog=None):
        """Slow fog-edge breath — distinct from placemarker + crumb pulses."""
        zoneId = int(zoneId)
        fog = self._fogEdges.get(zoneId) if fog is None else fog
        # Prefer the live fog edge for this zone (Func may pass a snapshot).
        live = self._fogEdges.get(zoneId)
        if live is not None:
            fog = live
        if not self._active or fog is None:
            return
        try:
            if fog.isEmpty():
                return
        except Exception:
            return
        self._stopFogPulse(zoneId)
        try:
            fog.setColorScale(_FOG_REST)
            fog.setScale(_FOG_SCALE)
        except Exception:
            pass
        gap = max(0.8, float(_FOG_PULSE_GAP_SEC))
        loop = Sequence(self._buildFogPulseIval(fog), Wait(gap))
        self._fogPulseIvals[zoneId] = loop
        try:
            loop.loop()
        except Exception:
            self._fogPulseIvals.pop(zoneId, None)
            try:
                fog.setColorScale(_FOG_REST)
                fog.setScale(_FOG_SCALE)
            except Exception:
                pass

    def _stopFogPulse(self, zoneId):
        zoneId = int(zoneId)
        ival = self._fogPulseIvals.pop(zoneId, None)
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
        self._stopCrumbPulse(zoneId)
        self._stopFogPulse(zoneId)
        ival = self._popIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                pass
        halo = self._pulseHalos.pop(zoneId, None)
        if halo is not None:
            try:
                halo.removeNode()
            except Exception:
                pass
        fog = self._fogEdges.pop(zoneId, None)
        if fog is not None:
            try:
                fog.removeNode()
            except Exception:
                pass
        trail = self._crumbTrails.pop(zoneId, None)
        if trail:
            # Remove trail root (parent of crumbs) when present.
            root = None
            try:
                root = trail[0].getParent()
            except Exception:
                root = None
            if root is not None:
                try:
                    if not root.isEmpty() and root.getName() == 'corruptStreetCrumbTrail':
                        root.removeNode()
                        trail = None
                except Exception:
                    pass
            if trail:
                for crumb in trail:
                    try:
                        crumb.removeNode()
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

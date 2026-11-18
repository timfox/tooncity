"""Plaza confront placemarker when TTC hub carries the betrayal stain.

Complements HubStain pollution fog: a short world TextNode + tip so the
hub consequence reads even before fog density settles. Not OswaldPresence
(trusted face) — this is the post-betrayal stain confront. No cream FX,
no KH branding.
"""

from __future__ import annotations

from panda3d.core import TextNode, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.campaign.HubStain import (
    hubStainEnabled,
    hubStainLevel,
    hubStainZone,
)
from toontown.corruption import CorruptionGlobals
from toontown.hood import ZoneUtil


def confrontEnabled():
    if not hubStainEnabled():
        return False
    return bool(getattr(CampaignGlobals, 'HUB_STAIN_CONFRONT_ENABLED', True))


def confrontLabel():
    return str(getattr(
        CampaignGlobals, 'HUB_STAIN_CONFRONT_LABEL',
        "Oswald's stain"))


def confrontTip():
    return str(getattr(
        CampaignGlobals, 'HUB_STAIN_CONFRONT_TIP',
        "Oswald's ink stains the plaza — wash the betrayal chase!  |  "
        'F fight  |  C campaign'))


def confrontForward():
    return float(getattr(
        CampaignGlobals, 'HUB_STAIN_CONFRONT_FORWARD', 5.5))


_MARKER_COLOR = Vec4(0.42, 0.18, 0.28, 1.0)  # ink-crimson, not trusted blue
_TIP_COLOR = Vec4(1.0, 0.92, 0.86, 1.0)


class HubStainConfrontClient(DirectObject):
    """Hub-only placemarker while HUB_ZONE pollution is stained."""

    def __init__(self):
        DirectObject.__init__(self)
        self._markerNP = None
        self._tipNP = None
        self._tipIval = None
        self._zoneId = None
        self._shown = False
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('pollutionChanged', self._onPollutionChanged)
        self.accept('hubStainApplied', self._onHubStainApplied)
        self.accept('hubStainCleared', self._onHubStainCleared)
        syncMsg = getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
            'campaignProgressSync')
        self.accept(syncMsg, self._onCampaignProgressSync)
        taskMgr.doMethodLater(  # noqa: F821
            2.35, self._bootZone, 'hubStainConfrontBoot')

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('hubStainConfrontBoot')  # noqa: F821
        except Exception:
            pass
        self._clearTip()
        self._clearMarker()
        self._zoneId = None
        self._shown = False

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def refreshHub(self):
        hub = hubStainZone()
        if hub > 0:
            self._onZoneChange(hub)

    def _onHubStainApplied(self, zoneId=None, level=0.0):
        self._refreshForHubPollution(float(level or 0.0))

    def _onHubStainCleared(self, zoneId=None):
        self._clearTip()
        self._clearMarker()
        self._shown = False

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0, reclaimCount=0):
        # Victory + uncleared chase → want confront; chase clear / replay → hide.
        # reclaimCount accepted for campaignProgressSync arity (power path).
        try:
            victory = int(state) == int(CampaignGlobals.STATE_VICTORY)
        except Exception:
            victory = False
        want = bool(
            confrontEnabled()
            and victory
            and int(chaseCleared or 0) == 0)
        if want:
            self.refreshHub()
        else:
            self._onHubStainCleared()

    def _onPollutionChanged(self, zoneId=None, level=None):
        try:
            zid = int(zoneId)
        except Exception:
            return
        if zid != hubStainZone():
            return
        self._refreshForHubPollution(float(level or 0.0))

    def _onZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):  # noqa: F821
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        try:
            zoneId = int(ZoneUtil.getBranchZone(int(zoneId)))
        except Exception:
            try:
                zoneId = int(zoneId)
            except Exception:
                return
        self._zoneId = zoneId
        if zoneId != hubStainZone() or not confrontEnabled():
            self._clearTip()
            self._clearMarker()
            self._shown = False
            return
        level = self._hubPollutionLevel()
        self._refreshForHubPollution(level)

    def _hubPollutionLevel(self):
        mgr = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if mgr is None:
            return 0.0
        try:
            return float(mgr.getPollution(hubStainZone()))
        except Exception:
            return 0.0

    def _refreshForHubPollution(self, level):
        if not confrontEnabled():
            return
        if self._zoneId is not None and self._zoneId != hubStainZone():
            return
        # If zone unknown, still allow hub refresh when on hub avatar.
        if self._zoneId is None:
            av = getattr(base, 'localAvatar', None)  # noqa: F821
            if av is not None:
                try:
                    self._zoneId = int(ZoneUtil.getBranchZone(int(av.zoneId)))
                except Exception:
                    pass
        if self._zoneId != hubStainZone():
            return
        if float(level) <= CorruptionGlobals.POLLUTION_PURE:
            # Progress sync may want confront before pollution mirrors —
            # fall back to authored stain level when victory pending.
            if not self._progressWantsConfront():
                self._clearTip()
                self._clearMarker()
                self._shown = False
                return
            level = hubStainLevel()
        if self._shown and self._markerNP is not None:
            return
        self._placeMarkerNearAvatar()
        self._flashTip()
        self._shown = True

    def _progressWantsConfront(self):
        mgr = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if mgr is None:
            return False
        try:
            state = int(getattr(mgr, 'campaignState', 0) or 0)
            cleared = int(getattr(mgr, 'campaignChaseCleared', 0) or 0)
        except Exception:
            return False
        return (
            state == int(CampaignGlobals.STATE_VICTORY)
            and cleared == 0)

    def _placeMarkerNearAvatar(self):
        self._clearMarker()
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        parent = getattr(base, 'render', None)  # noqa: F821
        if av is None or parent is None:
            return
        try:
            import math
            baseX = float(av.getX())
            baseY = float(av.getY())
            baseZ = float(av.getZ())
            heading = float(av.getH())
            rad = math.radians(heading)
            forward = confrontForward()
            x = baseX - math.sin(rad) * forward
            y = baseY + math.cos(rad) * forward
            z = baseZ + 1.15
        except Exception:
            return
        try:
            tn = TextNode('hubStainConfrontLabel')
            tn.setText(confrontLabel())
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(_MARKER_COLOR)
            np = parent.attachNewNode(tn)
            np.setPos(x, y, z)
            np.setBillboardPointEye()
            np.setScale(0.85)
            self._markerNP = np
        except Exception:
            self._markerNP = None

    def _flashTip(self):
        self._clearTip()
        tip = confrontTip()
        if not tip:
            return
        parent = getattr(base, 'aspect2d', None)  # noqa: F821
        if parent is None:
            return
        try:
            tn = TextNode('hubStainConfrontTip')
            tn.setText(tip)
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(_TIP_COLOR)
            np = parent.attachNewNode(tn)
            np.setScale(0.038)
            np.setPos(0.0, 0.0, -0.78)
            np.setTransparency(1)
            self._tipNP = np
            self._tipIval = Sequence(
                LerpScaleInterval(np, 0.08, 1.12, startScale=0.7),
                LerpScaleInterval(np, 0.10, 1.0),
                Wait(2.8),
                LerpColorScaleInterval(np, 0.35, Vec4(1, 1, 1, 0)),
                Func(self._clearTip))
            self._tipIval.start()
        except Exception:
            self._clearTip()

    def _clearTip(self):
        if self._tipIval is not None:
            try:
                self._tipIval.finish()
            except Exception:
                pass
            self._tipIval = None
        if self._tipNP is not None:
            try:
                self._tipNP.removeNode()
            except Exception:
                pass
            self._tipNP = None

    def _clearMarker(self):
        if self._markerNP is not None:
            try:
                self._markerNP.removeNode()
            except Exception:
                pass
            self._markerNP = None


_client = None


def ensureHubStainConfrontClient():
    global _client
    if not confrontEnabled():
        return None
    if _client is None:
        _client = HubStainConfrontClient()
    return _client


def refreshHubStainConfront():
    client = ensureHubStainConfrontClient()
    if client is not None:
        client.refreshHub()
    return client


def stopHubStainConfront():
    global _client
    if _client is not None:
        _client.destroy()
        _client = None

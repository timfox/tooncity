"""Washed-plaza epilogue beat after hub stain clear.

After Corrupted Oswald chase clear, TTC fog goes pristine again — this
module adds an authored world placemarker + tip so soft-end closure is
not HUD plate / HUB_VICTORY_TIP alone. Authored plaza stand
(HUB_EPILOGUE_BEAT_POS) — not near-avatar FORWARD. Complements
HubStainConfront (pending-stain confront) + OswaldPresence hub stand.
Celebration + Oswald absence confirmation on the washed plaza. After the
placemarker lands, sends hubEpilogueBeatShown; PlayEntry tip-latches the
post-wash F/C strip and OswaldPresence soft-clears the trusted face
(orphan → accept; no cream deepen). Toontown spiritual sequel — no KH
branding.
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
from toontown.campaign.HubStain import hubEpilogueBeatWanted, hubStainZone
from toontown.hood import ZoneUtil


def epilogueBeatEnabled():
    if not bool(getattr(CampaignGlobals, 'CAMPAIGN_EPILOGUE_ENABLED', True)):
        return False
    return bool(getattr(CampaignGlobals, 'HUB_EPILOGUE_BEAT_ENABLED', True))


def epilogueBeatLabel():
    return str(getattr(
        CampaignGlobals, 'HUB_EPILOGUE_BEAT_LABEL',
        'Plaza washed'))


def epilogueBeatAbsence():
    """Absence-confirmation line under the celebration label."""
    return str(getattr(
        CampaignGlobals, 'HUB_EPILOGUE_BEAT_ABSENCE',
        "Oswald's gone — plaza pure"))


def epilogueBeatTip():
    return str(getattr(
        CampaignGlobals, 'HUB_EPILOGUE_BEAT_TIP',
        "Toon Central plaza is washed clean — Oswald's absence holds. "
        'Replay from hub / C on Loopy!  |  F fight  |  C campaign'))


def epilogueBeatForward():
    return float(getattr(
        CampaignGlobals, 'HUB_EPILOGUE_BEAT_FORWARD', 5.5))


def epilogueBeatPlazaPos():
    """Authored TTC washed-plaza stand (x, y, z, h) or None if unset."""
    raw = getattr(CampaignGlobals, 'HUB_EPILOGUE_BEAT_POS', None)
    if raw is None:
        return None
    try:
        return (
            float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))
    except Exception:
        return None


# Re-export pure gate for callers / tests that import from this module.
__all__ = (
    'HubEpilogueBeatClient',
    'clearHubEpilogueBeat',
    'ensureHubEpilogueBeatClient',
    'epilogueBeatAbsence',
    'epilogueBeatEnabled',
    'epilogueBeatForward',
    'epilogueBeatLabel',
    'epilogueBeatPlazaPos',
    'epilogueBeatTip',
    'hubEpilogueBeatWanted',
    'refreshHubEpilogueBeat',
    'stopHubEpilogueBeat',
)


# Soft purity green — reclaim celebration, not ink-crimson confront.
_MARKER_COLOR = Vec4(0.35, 0.85, 0.62, 1.0)
_ABSENCE_COLOR = Vec4(0.72, 0.95, 0.88, 1.0)
_TIP_COLOR = Vec4(0.95, 1.0, 0.88, 1.0)


class HubEpilogueBeatClient(DirectObject):
    """Hub-only washed-plaza placemarker after chase-clear soft-end."""

    def __init__(self):
        DirectObject.__init__(self)
        self._markerNP = None
        self._absenceNP = None
        self._tipNP = None
        self._tipIval = None
        self._zoneId = None
        self._shown = False
        # Latch chase-clear so hub return works before PollutionManager
        # mirrors campaignChaseCleared (AI messenger is process-local).
        self._clearedLatched = False
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('hubStainCleared', self._onHubStainCleared)
        self.accept('hubStainApplied', self._onHubStainApplied)
        self.accept('oswaldBetrayalChaseCleared', self._onChaseCleared)
        self.accept('campaignEpilogue', self._onChaseCleared)
        syncMsg = getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
            'campaignProgressSync')
        self.accept(syncMsg, self._onCampaignProgressSync)
        taskMgr.doMethodLater(  # noqa: F821
            2.45, self._bootZone, 'hubEpilogueBeatBoot')

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('hubEpilogueBeatBoot')  # noqa: F821
        except Exception:
            pass
        self._clearTip()
        self._clearMarker()
        self._zoneId = None
        self._shown = False
        self._clearedLatched = False

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def refreshHub(self):
        hub = hubStainZone()
        if hub > 0:
            self._onZoneChange(hub)

    def _onHubStainApplied(self, zoneId=None, level=0.0):
        # Pending stain owns the plaza — hide washed-beat placemarker.
        self._clearedLatched = False
        self._hideBeat()

    def _onHubStainCleared(self, zoneId=None):
        # Fog wash alone is not enough — only show when chase is cleared.
        if self._progressWantsBeat():
            self.refreshHub()
        else:
            self._hideBeat()

    def _onChaseCleared(self, doId=0):
        if not epilogueBeatEnabled():
            return
        self._clearedLatched = True
        self.refreshHub()

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0, reclaimCount=0):
        # reclaimCount accepted for campaignProgressSync arity (power path).
        want = hubEpilogueBeatWanted(state, chaseCleared=chaseCleared)
        if want:
            self._clearedLatched = True
            self.refreshHub()
        else:
            self._clearedLatched = False
            self._hideBeat()

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
        if zoneId != hubStainZone() or not epilogueBeatEnabled():
            self._hideBeat()
            return
        if not self._progressWantsBeat():
            self._hideBeat()
            return
        if self._shown and self._markerNP is not None:
            return
        self._placeMarker()
        self._flashTip()
        self._shown = True
        # One-shot post-wash tip latch + Oswald soft-clear: PlayEntry /
        # OswaldPresence accept hubEpilogueBeatShown (orphan → accept).
        try:
            from toontown.campaign.PlayEntry import ensurePlayEntryClient
            ensurePlayEntryClient()
        except Exception:
            pass
        try:
            from toontown.campaign.OswaldPresence import (
                ensureOswaldPresenceClient)
            ensureOswaldPresenceClient()
        except Exception:
            pass
        shownMsg = getattr(
            CampaignGlobals, 'HUB_EPILOGUE_BEAT_SHOWN_MSG',
            'hubEpilogueBeatShown')
        try:
            messenger.send(shownMsg, [hubStainZone()])  # noqa: F821
        except Exception:
            pass

    def _progressWantsBeat(self):
        mgr = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if mgr is not None:
            try:
                state = int(getattr(mgr, 'campaignState', 0) or 0)
                cleared = int(getattr(mgr, 'campaignChaseCleared', 0) or 0)
                if hubEpilogueBeatWanted(state, chaseCleared=cleared):
                    return True
                # Explicit non-want from mirrored progress wins over latch
                # (replay wipe / mid-campaign hydrate).
                if state and int(state) != int(CampaignGlobals.STATE_VICTORY):
                    return False
                if int(state) == int(CampaignGlobals.STATE_VICTORY) and int(
                        cleared or 0) == 0:
                    return False
            except Exception:
                pass
        # Chase-clear messenger latched before PollutionManager mirrors.
        return bool(self._clearedLatched) and epilogueBeatEnabled()

    def _hideBeat(self):
        self._clearTip()
        self._clearMarker()
        self._shown = False

    def _placeMarker(self):
        """Authored plaza stand first; near-avatar FORWARD as fallback."""
        stand = epilogueBeatPlazaPos()
        if stand is not None:
            self._placeMarkerAtPlaza(stand)
            return
        self._placeMarkerNearAvatar()

    def _attachMarkerLabels(self, x, y, z, heading=None):
        self._clearMarker()
        parent = getattr(base, 'render', None)  # noqa: F821
        if parent is None:
            return
        try:
            tn = TextNode('hubEpilogueBeatLabel')
            tn.setText(epilogueBeatLabel())
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(_MARKER_COLOR)
            np = parent.attachNewNode(tn)
            np.setPos(x, y, z)
            if heading is not None:
                try:
                    np.setH(float(heading))
                except Exception:
                    pass
            np.setBillboardPointEye()
            np.setScale(0.85)
            self._markerNP = np
        except Exception:
            self._markerNP = None
            return
        absence = epilogueBeatAbsence()
        if not absence:
            return
        try:
            atn = TextNode('hubEpilogueBeatAbsence')
            atn.setText(absence)
            atn.setAlign(TextNode.ACenter)
            atn.setTextColor(_ABSENCE_COLOR)
            anp = parent.attachNewNode(atn)
            anp.setPos(x, y, z - 0.55)
            if heading is not None:
                try:
                    anp.setH(float(heading))
                except Exception:
                    pass
            anp.setBillboardPointEye()
            anp.setScale(0.55)
            self._absenceNP = anp
        except Exception:
            self._absenceNP = None

    def _placeMarkerAtPlaza(self, stand=None):
        """Place washed-plaza labels at authored HUB_EPILOGUE_BEAT_POS."""
        if stand is None:
            stand = epilogueBeatPlazaPos()
        if stand is None:
            return
        x, y, z, h = stand
        self._attachMarkerLabels(x, y, z, heading=h)

    def _placeMarkerNearAvatar(self):
        """Fallback when HUB_EPILOGUE_BEAT_POS is unset / unparseable."""
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None:
            return
        try:
            import math
            baseX = float(av.getX())
            baseY = float(av.getY())
            baseZ = float(av.getZ())
            heading = float(av.getH())
            rad = math.radians(heading)
            forward = epilogueBeatForward()
            x = baseX - math.sin(rad) * forward
            y = baseY + math.cos(rad) * forward
            z = baseZ + 1.15
        except Exception:
            return
        self._attachMarkerLabels(x, y, z)

    def _flashTip(self):
        self._clearTip()
        tip = epilogueBeatTip()
        if not tip:
            return
        parent = getattr(base, 'aspect2d', None)  # noqa: F821
        if parent is None:
            return
        try:
            tn = TextNode('hubEpilogueBeatTip')
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
        if self._absenceNP is not None:
            try:
                self._absenceNP.removeNode()
            except Exception:
                pass
            self._absenceNP = None
        if self._markerNP is not None:
            try:
                self._markerNP.removeNode()
            except Exception:
                pass
            self._markerNP = None


_client = None


def ensureHubEpilogueBeatClient():
    global _client
    if not epilogueBeatEnabled():
        return None
    if _client is None:
        _client = HubEpilogueBeatClient()
    return _client


def refreshHubEpilogueBeat():
    client = ensureHubEpilogueBeatClient()
    if client is not None:
        client.refreshHub()
    return client


def clearHubEpilogueBeat():
    """Drop washed-plaza placemarker (replay wipe / fresh campaign)."""
    if _client is not None:
        _client._clearedLatched = False
        _client._hideBeat()


def stopHubEpilogueBeat():
    global _client
    if _client is not None:
        _client.destroy()
        _client = None

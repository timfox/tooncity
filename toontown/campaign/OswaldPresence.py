"""Trusted Oswald hub/street presence stub before the twist.

Players meet Oswald as a world placemarker + proximity greet on the TTC
hub and campaign streets — the trust face they later lose at the finale
betrayal. Stub-shippable: not a DistributedNPC, not companion AI, not
cream FX. Suppresses after reveal / betrayal chase. Toontown spiritual
sequel — no keyblades / KH branding.
"""

from __future__ import annotations

import math

from panda3d.core import TextNode, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.hood import ZoneUtil


def presenceEnabled():
    return bool(getattr(CampaignGlobals, 'OSWALD_PRESENCE_ENABLED', True))


def presenceLabel():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_LABEL',
        getattr(CampaignGlobals, 'PROTAGONIST', 'Oswald')))


def presencePlate():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_PLATE', 'OSWALD'))


def hubGreetTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_HUB_GREET',
        'Oswald waves from the plaza — "Loopy Lane needs us first!"  |  '
        'Hop the tunnel  |  C campaign'))


def streetGreetTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_STREET_GREET',
        'Oswald tips his ears — "I\'ll field the packs — '
        'stretch-punch ready!"  |  '
        'F fight  |  Shift dodge  |  C campaign'))


def interactRadius():
    return max(2.0, float(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_INTERACT_RADIUS', 12.0)))


def spawnForward():
    return float(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_SPAWN_FORWARD', 6.5))


def spawnRight():
    return float(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_SPAWN_RIGHT', 2.25))


def hideOnBetrayal():
    return bool(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_HIDE_ON_BETRAYAL', True))


def presenceZoneIds():
    """Hub + campaign ACTS streets where the trusted stub may appear."""
    zones = set()
    hub = getattr(CampaignGlobals, 'HUB_ZONE', None)
    if hub is not None:
        zones.add(int(hub))
    for act in getattr(CampaignGlobals, 'ACTS', ()) or ():
        zid = act.get('zoneId')
        if zid is not None:
            zones.add(int(zid))
    return zones


def greetTipForZone(zoneId):
    """Hub vs street greet copy for the trusted Oswald stub."""
    hub = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
    try:
        zid = int(zoneId)
    except Exception:
        zid = -1
    if zid == hub:
        return hubGreetTip()
    return streetGreetTip()


def shouldShowPresence(zoneId, betrayed=False):
    """True when the trusted stub should be live in this zone."""
    if not presenceEnabled():
        return False
    if betrayed and hideOnBetrayal():
        return False
    try:
        zid = int(zoneId)
    except Exception:
        return False
    return zid in presenceZoneIds()


_MARKER_COLOR = Vec4(0.18, 0.52, 0.92, 1.0)
_TIP_COLOR = Vec4(0.95, 0.98, 1.0, 1.0)


class OswaldPresenceClient(DirectObject):
    """World placemarker + proximity greet for trusted Oswald.

    AI-free stub: place near the local toon on hub/street enter, greet
    once per zone visit when approached, clear after betrayal messengers.
    """

    def __init__(self):
        DirectObject.__init__(self)
        self._markerNP = None
        self._tipNP = None
        self._tipIval = None
        self._zoneId = None
        self._greetedZone = None
        self._betrayed = False
        self._markerPos = None
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('oswaldRevealBanner', self._onBetrayal)
        self.accept('oswaldRevealSting', self._onBetrayal)
        self.accept('campaignVictory', self._onBetrayal)
        self.accept('oswaldBetrayalChase', self._onBetrayal)
        # Login mirror — AI-persisted STATE_VICTORY must hide trusted Oswald
        # after relog (session-only `_betrayed` is not enough).
        syncMsg = getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
            'campaignProgressSync')
        self.accept(syncMsg, self._onCampaignProgressSync)
        taskMgr.doMethodLater(  # noqa: F821
            2.15, self._bootZone, 'oswaldPresenceBoot')

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('oswaldPresenceBoot')  # noqa: F821
        except Exception:
            pass
        self._stopPoll()
        self._clearTip()
        self._clearMarker()
        self._zoneId = None
        self._greetedZone = None
        self._betrayed = False

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def _onBetrayal(self, *args):
        if not hideOnBetrayal():
            return
        self._betrayed = True
        self._stopPoll()
        self._clearTip()
        self._clearMarker()
        self._zoneId = None
        self._greetedZone = None

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0):
        """Apply AI-persisted victory so trusted presence survives relog."""
        try:
            from toontown.campaign import CampaignProgressSave
            mirror = CampaignProgressSave.clientMirrorFromProgress({
                'unlockedThrough': unlockedThrough,
                'state': state,
                'chaseCleared': chaseCleared,
            })
        except Exception:
            return
        betrayed = bool(mirror.get('betrayed'))
        if betrayed:
            if not self._betrayed:
                self._onBetrayal()
            else:
                self._betrayed = True
            return
        # Fresh / mid-campaign — trusted face may return (replay wipe).
        wasBetrayed = self._betrayed
        self._betrayed = False
        if wasBetrayed:
            # Re-arm marker in the current zone after a replay wipe sync.
            self._onZoneChange(self._zoneId)

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
        self._stopPoll()
        self._clearTip()
        self._clearMarker()
        self._zoneId = zoneId
        if not shouldShowPresence(zoneId, betrayed=self._betrayed):
            return
        self._placeMarkerNearAvatar(zoneId)
        self._startPoll()

    def refreshHub(self):
        """Optional hub re-arm (TTPlayground enter)."""
        hub = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
        if hub > 0:
            self._onZoneChange(hub)

    def _placeMarkerNearAvatar(self, zoneId):
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        parent = getattr(base, 'render', None)  # noqa: F821
        if av is None or parent is None:
            return
        try:
            baseX = float(av.getX())
            baseY = float(av.getY())
            baseZ = float(av.getZ())
            heading = float(av.getH())
        except Exception:
            return
        rad = math.radians(heading)
        forward = spawnForward()
        right = spawnRight()
        # Forward of facing + slight right so the stub reads beside the path.
        x = baseX - math.sin(rad) * forward + math.cos(rad) * right
        y = baseY + math.cos(rad) * forward + math.sin(rad) * right
        z = baseZ + float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_MARKER_Z', 2.8))

        color = getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_MARKER_COLOR', None)
        if color is None:
            color = _MARKER_COLOR
        else:
            color = Vec4(
                float(color[0]), float(color[1]),
                float(color[2]), float(color[3]))

        tn = TextNode('oswaldPresenceLabel')
        tn.setText(presenceLabel())
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(color)
        try:
            tn.setShadow(0.04, 0.04)
            tn.setShadowColor(0.05, 0.12, 0.28, 0.55)
        except Exception:
            pass
        np = parent.attachNewNode(tn)
        np.setPos(x, y, z)
        np.setScale(float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_MARKER_SCALE', 1.2)))
        try:
            np.setBillboardPointEye()
        except Exception:
            pass
        # Soft rubber-hose appear pop.
        try:
            np.setScale(np.getScale() * 0.55)
            scale = float(getattr(
                CampaignGlobals, 'OSWALD_PRESENCE_MARKER_SCALE', 1.2))
            Sequence(
                LerpScaleInterval(np, 0.12, scale * 1.18),
                LerpScaleInterval(np, 0.10, scale),
                name='oswaldPresencePop',
            ).start()
        except Exception:
            pass
        self._markerNP = np
        self._markerPos = (x, y, baseZ)

    def _pollTaskName(self):
        return 'oswaldPresencePoll'

    def _startPoll(self):
        self._stopPoll()
        delay = max(0.15, float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_POLL_SEC', 0.35)))
        taskMgr.doMethodLater(  # noqa: F821
            delay, self._pollProximity, self._pollTaskName())

    def _stopPoll(self):
        try:
            taskMgr.remove(self._pollTaskName())  # noqa: F821
        except Exception:
            pass

    def _pollProximity(self, task):
        zoneId = self._zoneId
        if zoneId is None or not shouldShowPresence(
                zoneId, betrayed=self._betrayed):
            return task.done
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return task.again
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or self._markerPos is None:
            return task.again
        try:
            ax = float(av.getX())
            ay = float(av.getY())
        except Exception:
            return task.again
        mx, my, _mz = self._markerPos
        dist = math.hypot(ax - mx, ay - my)
        if dist <= interactRadius():
            self._meetOswald(zoneId)
        return task.again

    def _meetOswald(self, zoneId):
        """Proximity greet — meetable trust face beat (once per zone visit)."""
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return
        self._greetedZone = int(zoneId)
        tip = greetTipForZone(zoneId)
        self._showGreetTip(tip)
        try:
            messenger.send(  # noqa: F821
                'oswaldPresenceMet', [int(zoneId), presenceLabel()])
        except Exception:
            pass

    def _showGreetTip(self, tip):
        self._clearTip()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return
        color = getattr(CampaignGlobals, 'OSWALD_PRESENCE_TIP_COLOR', None)
        if color is None:
            tipColor = _TIP_COLOR
        else:
            tipColor = Vec4(
                float(color[0]), float(color[1]),
                float(color[2]), float(color[3]))
        tn = TextNode('oswaldPresenceTip')
        tn.setText(str(tip))
        tn.setAlign(TextNode.ACenter)
        tn.setWordwrap(28)
        tn.setTextColor(tipColor)
        tipNP = parent.attachNewNode(tn)
        tipNP.setScale(0.045)
        tipNP.setPos(0.0, 0.0, -0.78)
        tipNP.setColorScale(1, 1, 1, 0)
        self._tipNP = tipNP
        hold = max(1.0, float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_GREET_HOLD_SEC', 3.2)))
        pop = Parallel(
            Sequence(
                LerpScaleInterval(tipNP, 0.08, 0.052),
                LerpScaleInterval(tipNP, 0.10, 0.045),
            ),
            LerpColorScaleInterval(tipNP, 0.12, Vec4(1, 1, 1, 1)),
        )
        self._tipIval = Sequence(
            pop,
            Wait(hold),
            LerpColorScaleInterval(tipNP, 0.28, Vec4(1, 1, 1, 0)),
            Func(self._clearTip),
            name='oswaldPresenceGreetTip',
        )
        self._tipIval.start()

    def _clearTip(self):
        if self._tipIval is not None:
            try:
                self._tipIval.pause()
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
        self._markerPos = None


_client = None


def ensureOswaldPresenceClient():
    global _client
    if _client is None:
        _client = OswaldPresenceClient()
    return _client


def refreshOswaldPresenceHub():
    """Thin hub re-arm for TTPlayground enter."""
    client = ensureOswaldPresenceClient()
    try:
        client.refreshHub()
    except Exception:
        pass
    return client


def stopOswaldPresenceClient():
    """Optional teardown (playground exit) — keeps singleton for re-enter."""
    global _client
    if _client is None:
        return
    try:
        _client._stopPoll()
        _client._clearTip()
        _client._clearMarker()
    except Exception:
        pass

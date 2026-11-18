"""Discoverable KH×Toontown loop entry — no magic-word memorization required.

On campaign streets: auto-arm melee, show prompts, bind R/C to start reclaim/campaign
via PollutionManager.requestStreetEvent.
"""

from panda3d.core import TextNode, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals


class PlayEntryClient(DirectObject):
    """Player-facing entry prompts + auto melee on corrupt streets."""

    def __init__(self):
        DirectObject.__init__(self)
        self._tipNP = None
        self._flashNP = None
        self._flashIval = None
        self._armedZone = None
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('announceReclaimStart', self._onReclaimStart)
        # Reclaim director also shows banners; listen for DO messenger-less path:
        self.accept('purityRestoreFx', self._onPurity)
        taskMgr.doMethodLater(2.0, self._bootZone, 'playEntryBoot')  # noqa: F821

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('playEntryBoot')  # noqa: F821
        except Exception:
            pass
        self._clearTip()
        self._clearFlash()
        self.ignore('r')
        self.ignore('c')

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def _campaignZoneIds(self):
        return {int(a['zoneId']) for a in CampaignGlobals.ACTS}

    def _onZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):  # noqa: F821
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        zoneId = int(zoneId)
        if zoneId not in self._campaignZoneIds():
            self._clearTip()
            self.ignore('r')
            self.ignore('c')
            self._armedZone = None
            return
        self._armMelee(zoneId)
        act = self._actForZone(zoneId)
        name = act['name'] if act else 'this street'
        self._showTip(
            'CORRUPTION on %s — F fight  |  Shift dodge  |  R reclaim  |  C campaign'
            % name)
        self.accept('r', self._requestReclaim)
        self.accept('c', self._requestCampaign)

    def _actForZone(self, zoneId):
        for act in CampaignGlobals.ACTS:
            if int(act['zoneId']) == int(zoneId):
                return act
        return None

    def _armMelee(self, zoneId):
        if self._armedZone == zoneId:
            return
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or not hasattr(av, 'enableHackSlashMelee'):
            return
        try:
            av.enableHackSlashMelee(spawnHostiles=False)
            self._armedZone = zoneId
            self._flashBanner('MELEE ARMED — Press F / LMB')
        except Exception:
            pass

    def _onReclaimStart(self, *args):
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is not None and hasattr(av, 'enableHackSlashMelee'):
            try:
                av.enableHackSlashMelee(spawnHostiles=False)
            except Exception:
                pass
        self._flashBanner('RECLAIM LIVE — Clear Corrupt Toons with F!')

    def _onPurity(self, zoneId):
        self._flashBanner('STREET PURIFIED — Head to the next hood!')

    def _requestReclaim(self):
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return
        pm.d_requestStreetEvent(0)
        self._flashBanner('Calling street reclaim…')

    def _requestCampaign(self):
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return
        pm.d_requestStreetEvent(1)
        self._flashBanner('Calling campaign act…')

    def _showTip(self, text):
        self._clearTip()
        tn = TextNode('play-entry-tip')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 0.95, 0.55, 1)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(0.042)
        np.setPos(0, 0, -0.92)
        self._tipNP = np

    def _clearTip(self):
        if self._tipNP and not self._tipNP.isEmpty():
            self._tipNP.removeNode()
        self._tipNP = None

    def _flashBanner(self, text):
        self._clearFlash()
        tn = TextNode('play-entry-flash')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 0.85, 1, 1)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.8)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(0.06)
        np.setPos(0, 0, 0.72)
        np.setColorScale(1, 1, 1, 0)
        self._flashNP = np
        self._flashIval = Sequence(
            LerpColorScaleInterval(np, 0.15, Vec4(1, 1, 1, 1)),
            Wait(2.4),
            LerpColorScaleInterval(np, 0.35, Vec4(1, 1, 1, 0)),
            Func(self._clearFlash),
        )
        self._flashIval.start()

    def _clearFlash(self):
        if self._flashIval:
            try:
                self._flashIval.pause()
            except Exception:
                pass
            self._flashIval = None
        if self._flashNP and not self._flashNP.isEmpty():
            self._flashNP.removeNode()
        self._flashNP = None


_client = None


def ensurePlayEntryClient():
    global _client
    if _client is None:
        _client = PlayEntryClient()
    return _client

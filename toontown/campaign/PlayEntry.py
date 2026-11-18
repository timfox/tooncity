"""Discoverable Toon City loop entry — no magic-word memorization required.

Oswald leads the reclaim fantasy in tip/banner copy. On campaign streets:
auto-arm melee, auto-start reclaim packs (no ~spawncorrupt), show prompts,
bind R/C to reclaim/campaign via PollutionManager.requestStreetEvent.

On polluted ACTS street enter: brief rubber-hose ink edge vignette that
fades as the tip bar appears (Toontown spiritual sequel — no KH branding).
"""

from panda3d.core import CardMaker, TextNode, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.corruption import CorruptionGlobals

# Brief delay so zone + PollutionManager are ready before auto-fielding packs.
AUTO_RECLAIM_DELAY_SEC = 1.35


def _face():
    return getattr(
        CampaignGlobals, 'RECLAIM_FACE',
        getattr(CampaignGlobals, 'PROTAGONIST', 'Oswald'))


class PlayEntryClient(DirectObject):
    """Player-facing entry prompts + auto melee on corrupt streets."""

    def __init__(self):
        DirectObject.__init__(self)
        self._tipNP = None
        self._tipIval = None
        self._flashNP = None
        self._flashIval = None
        self._vignetteRoot = None
        self._vignetteIval = None
        self._armedZone = None
        self._autoReclaimZone = None
        self._reclaimLive = False
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('announceReclaimStart', self._onReclaimStart)
        # CampaignHandoff owns the celebration; tip bar latches the next cue.
        self.accept('purityRestoreFx', self._onPurity)
        self.accept('campaignHandoffCue', self._onHandoffCue)
        try:
            from toontown.reclaim.ReclaimCheer import ensureReclaimCheerClient
            ensureReclaimCheerClient()
        except Exception:
            pass
        try:
            from toontown.reclaim.PurityBurstFx import ensurePurityBurstFxClient
            ensurePurityBurstFxClient()
        except Exception:
            pass
        try:
            from toontown.campaign.CampaignHandoff import (
                ensureCampaignHandoffClient)
            ensureCampaignHandoffClient()
        except Exception:
            pass
        taskMgr.doMethodLater(2.0, self._bootZone, 'playEntryBoot')  # noqa: F821

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('playEntryBoot')  # noqa: F821
        except Exception:
            pass
        self._cancelAutoReclaim()
        self._clearTip()
        self._clearFlash()
        self._clearVignette()
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
        self._cancelAutoReclaim()
        self._reclaimLive = False
        if zoneId not in self._campaignZoneIds():
            self._clearTip()
            self._clearVignette()
            self.ignore('r')
            self.ignore('c')
            self._armedZone = None
            self._autoReclaimZone = None
            return
        self._armMelee(zoneId)
        act = self._actForZone(zoneId)
        name = act['name'] if act else 'this street'
        face = _face()
        tip = (
            '%s: CORRUPTION on %s — packs incoming  |  '
            'F fight  |  Shift dodge  |  C campaign' % (face, name))
        if act and act.get('finale'):
            tip = (
                '%s vs the Ink Overlord on %s  |  '
                'F fight  |  Shift dodge  |  C campaign' % (face, name))
        # Ink edge vignette on polluted ACTS enter; tip fades in as it clears.
        if self._streetIsPolluted(zoneId):
            self._playEntryVignette(zoneId, tip)
        else:
            self._clearVignette()
            self._showTip(tip)
        self.accept('r', self._requestReclaim)
        self.accept('c', self._requestCampaign)
        # Auto-field reclaim waves so hostiles appear without ~spawncorrupt / R.
        self._autoReclaimZone = zoneId
        taskMgr.doMethodLater(  # noqa: F821
            AUTO_RECLAIM_DELAY_SEC,
            self._autoStartReclaim,
            self._autoReclaimTaskName(zoneId))

    def _streetIsPolluted(self, zoneId):
        """True when local pollution (or act seed) still stains the street."""
        minLevel = float(CorruptionGlobals.ENTRY_VIGNETTE_MIN_POLLUTION)
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is not None:
            try:
                level = float(pm.getPollution(zoneId))
                if level >= minLevel:
                    return True
                # Known pure (reclaim cleared) — skip vignette.
                if zoneId in getattr(pm, 'zonePollution', {}):
                    return False
            except Exception:
                pass
        act = self._actForZone(zoneId)
        if act is None:
            return False
        return float(act.get('seedPollution', 0.0)) >= minLevel

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
            # Keep #33 stretch-punch combat framing (no keyblade / KH copy).
            self._flashBanner(
                '%s: STRETCH PUNCHES — Press F / LMB' % _face())
        except Exception:
            pass

    def _autoReclaimTaskName(self, zoneId):
        return 'playEntryAutoReclaim-%s' % int(zoneId)

    def _cancelAutoReclaim(self):
        zoneId = self._autoReclaimZone
        if zoneId is None:
            return
        try:
            taskMgr.remove(self._autoReclaimTaskName(zoneId))  # noqa: F821
        except Exception:
            pass

    def _autoStartReclaim(self, task):
        """Kick reclaim once per street enter so packs field without magic words."""
        zoneId = self._autoReclaimZone
        if zoneId is None:
            return task.done
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or int(getattr(av, 'zoneId', -1)) != int(zoneId):
            return task.done
        if self._reclaimLive:
            return task.done
        self._requestReclaim()
        self._flashBanner('%s fields the packs — Fight!' % _face())
        return task.done

    def _onReclaimStart(self, *args):
        self._reclaimLive = True
        self._cancelAutoReclaim()
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is not None and hasattr(av, 'enableHackSlashMelee'):
            try:
                av.enableHackSlashMelee(spawnHostiles=False)
            except Exception:
                pass
        self._flashBanner(
            'RECLAIM LIVE — %s says clear them with F!' % _face())

    def _onPurity(self, zoneId):
        """Yield the celebration banner to CampaignHandoff; tip shows next street."""
        self._reclaimLive = False
        act, nxt = self._actsAroundZone(zoneId)
        face = _face()
        if act and act.get('finale'):
            tip = act.get('nextCue') or (
                getattr(CampaignGlobals, 'FINALE_TWIST_TEASE', None)
                or "%s's smile feels… wrong" % face)
        elif act and act.get('nextCue'):
            tip = act['nextCue']
        elif nxt is not None:
            tip = '%s points the tunnel → %s' % (
                face, nxt.get('name', 'the next street'))
        else:
            tip = '%s cheers — purity holds!' % face
        # Persist next-street / twist cue on the tip bar (no competing toast).
        self._showTip('%s  |  F fight  |  C campaign' % tip)

    def _onHandoffCue(self, nextStreet=None, cueText=None):
        """Latch CampaignHandoff's next-street beat onto the tip bar."""
        text = cueText
        if not text and nextStreet:
            text = '%s points the way → %s' % (_face(), nextStreet)
        if text:
            self._showTip('%s  |  F fight  |  C campaign' % text)

    def _actsAroundZone(self, zoneId):
        if zoneId is None:
            return None, None
        zoneId = int(zoneId)
        for i, act in enumerate(CampaignGlobals.ACTS):
            if int(act['zoneId']) == zoneId:
                nxt = (
                    CampaignGlobals.ACTS[i + 1]
                    if i + 1 < len(CampaignGlobals.ACTS) else None)
                return act, nxt
        return None, None

    def _requestReclaim(self):
        if self._reclaimLive:
            return
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return
        pm.d_requestStreetEvent(0)
        self._flashBanner('%s is calling street reclaim…' % _face())

    def _requestCampaign(self):
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return
        pm.d_requestStreetEvent(1)
        self._flashBanner('%s is calling the next act…' % _face())

    def _playEntryVignette(self, zoneId, tipText):
        """Brief ink edge darken that fades as the tip bar appears."""
        self._clearVignette()
        root = self._buildVignetteRoot(zoneId)
        if root is None:
            self._showTip(tipText)
            return
        self._vignetteRoot = root
        # Tip starts invisible, fades in while vignette holds/fades out.
        self._showTip(tipText, fadeIn=True)
        tipNP = self._tipNP
        inSec = float(CorruptionGlobals.ENTRY_VIGNETTE_IN_SEC)
        holdSec = float(CorruptionGlobals.ENTRY_VIGNETTE_HOLD_SEC)
        outSec = float(CorruptionGlobals.ENTRY_VIGNETTE_OUT_SEC)
        tipDelay = float(CorruptionGlobals.ENTRY_VIGNETTE_TIP_DELAY_SEC)
        tipFade = float(CorruptionGlobals.ENTRY_VIGNETTE_TIP_FADE_SEC)
        peak = float(CorruptionGlobals.ENTRY_VIGNETTE_PEAK_ALPHA)

        parts = [
            Sequence(
                LerpColorScaleInterval(root, inSec, Vec4(1, 1, 1, peak)),
                Wait(holdSec),
                LerpColorScaleInterval(root, outSec, Vec4(1, 1, 1, 0)),
                Func(self._clearVignette),
            ),
        ]
        if tipNP is not None and not tipNP.isEmpty():
            parts.append(Sequence(
                Wait(tipDelay),
                LerpColorScaleInterval(tipNP, tipFade, Vec4(1, 1, 1, 1)),
            ))
        self._vignetteIval = Sequence(
            Parallel(*parts),
            name='playEntryInkVignette',
        )
        self._vignetteIval.start()

    def _buildVignetteRoot(self, zoneId):
        """Four ink edge strips — rubber-hose frame darken, open center."""
        try:
            ink = CorruptionGlobals.entryVignetteInk(zoneId)
            edge = float(CorruptionGlobals.ENTRY_VIGNETTE_EDGE)
            binSort = int(CorruptionGlobals.ENTRY_VIGNETTE_BIN)
            root = aspect2d.attachNewNode('play-entry-ink-vignette')  # noqa: F821
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', binSort)
            root.setDepthTest(False)
            root.setDepthWrite(False)
            # Top / bottom / left / right — thick ink borders, clear middle.
            frames = (
                (-2.0, 2.0, 1.0 - edge, 1.25),
                (-2.0, 2.0, -1.25, -1.0 + edge),
                (-2.0, -1.0 + edge, -1.25, 1.25),
                (1.0 - edge, 2.0, -1.25, 1.25),
            )
            for i, frame in enumerate(frames):
                cm = CardMaker('play-entry-vignette-%s' % i)
                cm.setFrame(*frame)
                strip = root.attachNewNode(cm.generate())
                strip.setTransparency(TransparencyAttrib.MAlpha)
                strip.setColor(ink[0], ink[1], ink[2], 1)
                strip.setBin('fixed', binSort)
                strip.setDepthTest(False)
                strip.setDepthWrite(False)
            return root
        except Exception:
            return None

    def _clearVignette(self):
        if self._vignetteIval:
            try:
                self._vignetteIval.pause()
            except Exception:
                pass
            self._vignetteIval = None
        root = self._vignetteRoot
        self._vignetteRoot = None
        if root is not None:
            try:
                if not root.isEmpty():
                    root.removeNode()
            except Exception:
                pass

    def _showTip(self, text, fadeIn=False):
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
        if fadeIn:
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColorScale(1, 1, 1, 0)
        self._tipNP = np

    def _clearTip(self):
        if self._tipIval:
            try:
                self._tipIval.pause()
            except Exception:
                pass
            self._tipIval = None
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

"""Discoverable Toon City loop entry — no magic-word memorization required.

Oswald leads the reclaim fantasy in tip/banner copy **and** a hub/street
NPC-style presence stub (`OswaldPresence` — body + short E-talk greet)
so the player meets the trusted lead before the twist. On the TTC hub:
tip points at the next reclaim street (Loopy first; soft handoff cue after).
On campaign streets: auto-arm melee, auto-start the **campaign** act (C
path — not street-pack R) so packs field without ~startcampaign / racing
C vs auto-reclaim, show prompts, bind R/C via PollutionManager.
Loopy Act 1 keeps a trusted early street tip, then a delayed mid-act
unease approach tip (smile sticks a rubbery half-beat) before Punchline
handoff — foreshadow only, no Silly twist spoilers / no KH branding.

On polluted ACTS street enter: brief rubber-hose ink edge vignette that
fades as the tip bar appears. Tip bar and act-enter flash banners play a
short rubber-hose scale pop when they land. Act-enter ACTS banners also
pulse a soft cream edge frame + tip flecks (wave-announce cream edge twin).
Early/mid Oswald trusted reclaim-lead act banners add a soft settle bounce
after that pop.
Punchline Place Act 2 uses a campaign-owned entry tip (Brute/Snare cues,
trusted Oswald lead / unease) with a slightly punchier tip hose pop +
trust/fracture settle, a deepened cream hose settle past #256 (juicier
overshoot → rest → micro rebound) so the Act 2 unease tip lands
rubber-hose and reads juicier, and a delayed soft cream wash pulse
(act-banner / trust wash twin). Distinct from Silly almost-confess tip
cream hose (#232/#279) and Silly Overlord tip cream wash aftershock
(#251/#279).
Silly Street Act 3 uses a campaign-owned entry tip (Ink Overlord cues,
cheer-feels-wrong foreshadow) with a slightly heavier tip hose pop +
fracture trust settle, a deepened cream hose settle past #279 so the
trust-fracture / almost-confess tip lands rubber-hose and clear
(taller/longer primary overshoot; no tip rebound — Punchline deepen owns
that; betrayal banner owns climax rebound), and a deepened delayed soft
cream wash pulse + cream aftershock past #279; a mid-act approach tip
then almost-confesses an uneasy half-truth before the finale reveal
(Punchline tip / act-banner wash twin; FinalePhaseFx betrayal banner
stays separate — no KH branding).
"""

from panda3d.core import (
    CardMaker, Point3, TextNode, TransparencyAttrib, Vec4)

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
from toontown.corruption import CorruptionGlobals
from toontown.hood import ZoneUtil
from toontown.reclaim import ReclaimGlobals

# Brief delay so zone + PollutionManager are ready before auto-fielding packs.
AUTO_RECLAIM_DELAY_SEC = 1.35
# Loopy Act 1 tutorial: short explore beat before Ink Smudge packs field.
LOOPY_AUTO_RECLAIM_DELAY_SEC = 1.55
# Punchline sludge street: slightly longer explore beat before packs field.
PUNCHLINE_AUTO_RECLAIM_DELAY_SEC = 1.85
# Silly Overlord finale: longer explore beat before Overlord packs field.
SILLY_AUTO_RECLAIM_DELAY_SEC = 2.15
# Fallback if CampaignGlobals.SILLY_APPROACH_TIP_DELAY_SEC is missing.
_SILLY_APPROACH_TIP_DELAY_FALLBACK_SEC = 3.85
# Fallback if CampaignGlobals.LOOPY_APPROACH_TIP_DELAY_SEC is missing.
_LOOPY_APPROACH_TIP_DELAY_FALLBACK_SEC = 3.45


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
        self._approachTipZone = None
        self._loopyApproachTipZone = None
        self._reclaimLive = False
        # Soft next-street cue survives hub / playground hops until the
        # pointed ACTS street is entered (no magic words / zone ids).
        self._softNextCue = None
        self._softNextZone = None
        self._softNextStreet = None
        # After STATE_VICTORY / chase-clear epilogue, hub tip uses replay copy.
        # Also latched from AI CampaignProgressSave via campaignProgressSync
        # so relog mirrors victory / unlock (not process-local only).
        # chasePending (victory + chaseCleared=0) keeps hub tip from claiming
        # the stain is washed before the betrayal chase clears.
        self._victoryEpilogue = False
        self._chasePending = False
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('announceReclaimStart', self._onReclaimStart)
        # KO fail (#323) — clear live latch so same-street R / re-enter retry.
        self.accept('announceReclaimFailed', self._onReclaimFailed)
        # CampaignHandoff owns the celebration; tip bar latches the next cue.
        self.accept('purityRestoreFx', self._onPurity)
        self.accept('campaignHandoffCue', self._onHandoffCue)
        self.accept('campaignVictory', self._onCampaignVictory)
        self.accept('oswaldBetrayalChaseCleared', self._onCampaignEpilogue)
        self.accept('campaignEpilogue', self._onCampaignEpilogue)
        # Soft-gate unlock → hub crumbs (dim → full). AI also sends; purity
        # mirror below covers real client processes where AI messenger is local.
        self.accept('campaignActUnlocked', self._onCampaignActUnlocked)
        # Login mirror — AI-persisted victory / unlock / chaseCleared.
        syncMsg = getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
            'campaignProgressSync')
        self.accept(syncMsg, self._onCampaignProgressSync)
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
        try:
            from toontown.campaign.OswaldBetrayalChase import (
                ensureOswaldBetrayalChaseClient)
            ensureOswaldBetrayalChaseClient()
        except Exception:
            pass
        try:
            from toontown.campaign.OswaldPresence import (
                ensureOswaldPresenceClient)
            ensureOswaldPresenceClient()
        except Exception:
            pass
        taskMgr.doMethodLater(2.0, self._bootZone, 'playEntryBoot')  # noqa: F821
        # Login mirror — ask AI for persisted victory / unlock / chaseCleared
        # so hub tip matches story before the player presses C/R.
        taskMgr.doMethodLater(  # noqa: F821
            2.25, self._bootCampaignProgress, 'playEntryCampaignProgress')

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('playEntryBoot')  # noqa: F821
        except Exception:
            pass
        try:
            taskMgr.remove('playEntryCampaignProgress')  # noqa: F821
        except Exception:
            pass
        self._cancelAutoReclaim()
        self._cancelSillyApproachTip()
        self._cancelLoopyApproachTip()
        self._clearTip()
        self._clearFlash()
        self._clearVignette()
        self.ignore('r')
        self.ignore('c')

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def _bootCampaignProgress(self, task):
        """Request thin PollutionManager campaign progress push after login."""
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is not None and hasattr(pm, 'd_requestCampaignProgress'):
            try:
                pm.d_requestCampaignProgress()
            except Exception:
                pass
        return task.done

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0, reclaimCount=0):
        """Apply AI-persisted progress so hub tip survives relog."""
        try:
            from toontown.campaign import CampaignProgressSave
            mirror = CampaignProgressSave.clientMirrorFromProgress({
                'unlockedThrough': unlockedThrough,
                'state': state,
                'chaseCleared': chaseCleared,
                'reclaimCount': reclaimCount,
                # actIndex omitted — sanitize uses unlockedThrough as default.
            })
        except Exception:
            return
        self._victoryEpilogue = bool(mirror.get('victoryEpilogue'))
        self._chasePending = bool(mirror.get('chasePending'))
        if self._victoryEpilogue:
            # Victory / chase soft-end — drop mid-act soft cues.
            self._softNextCue = None
            self._softNextZone = None
            self._softNextStreet = None
        else:
            self._chasePending = False
            softStreet = mirror.get('softNextStreet')
            if softStreet:
                self._softNextStreet = softStreet
                self._softNextCue = None
            elif int(mirror.get('unlockedThrough', 0) or 0) <= 0:
                # Fresh campaign — clear stale soft cues from a prior local
                # session if the AI says Act 1 only.
                self._softNextStreet = None
        # Refresh hub tip if the player is already on TTC.
        hubZone = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is not None and hubZone > 0:
            try:
                zoneId = int(ZoneUtil.getBranchZone(
                    int(getattr(av, 'zoneId', 0) or 0)))
            except Exception:
                zoneId = int(getattr(av, 'zoneId', 0) or 0)
            if zoneId == hubZone:
                self._showHubTip()

    def _campaignZoneIds(self):
        return {int(a['zoneId']) for a in CampaignGlobals.ACTS}

    def _onZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):  # noqa: F821
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        # Branch zone so ACTS / STREET_PACKS match (boot may see floor ids).
        try:
            zoneId = int(ZoneUtil.getBranchZone(int(zoneId)))
        except Exception:
            zoneId = int(zoneId)
        self._cancelAutoReclaim()
        self._cancelSillyApproachTip()
        self._cancelLoopyApproachTip()
        self._reclaimLive = False
        hubZone = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
        if zoneId == hubZone:
            self._showHubTip()
            self._clearVignette()
            self.ignore('r')
            self.accept('c', self._requestCampaign)
            self._armedZone = None
            self._autoReclaimZone = None
            return
        if zoneId not in self._campaignZoneIds():
            # Soft next-street cue survives playground hops.
            if self._softNextCue:
                self._showTip(self._softNextCue)
            else:
                self._clearTip()
            self._clearVignette()
            self.ignore('r')
            self.ignore('c')
            self._armedZone = None
            self._autoReclaimZone = None
            return
        # Arrived at the handoff street — clear soft hub cue.
        if self._softNextZone is not None and zoneId == int(self._softNextZone):
            self._softNextCue = None
            self._softNextZone = None
            self._softNextStreet = None
        self._armMelee(zoneId)
        act = self._actForZone(zoneId)
        name = act['name'] if act else 'this street'
        face = _face()
        tipHose = None
        # Campaign ACTS entryTip wins (Punchline Act 2 sludge mix + Oswald
        # unease tip; Silly Act 3 Ink Overlord + cheer-feels-wrong foreshadow).
        # Else STREET_PACK tip; Loopy Act 1 keeps trusted street tip early.
        # Finale also arms a delayed mid-act approachTip (almost-confess).
        # Loopy arms a delayed mid-act unease approachTip before Punchline.
        if act and act.get('entryTip'):
            tip = act['entryTip']
            if act.get('id') == 'punchline':
                tipHose = 'punchline'
            elif act.get('id') == 'finale':
                tipHose = 'silly'
        else:
            pack = ReclaimGlobals.streetPack(zoneId)
            if pack and pack.get('playEntryTip'):
                tip = ReclaimGlobals.streetPlayEntryTip(
                    zoneId, face=face, fallbackName=name)
            elif act and act.get('finale'):
                tip = (
                    '%s vs the Ink Overlord on %s  |  '
                    'F fight  |  Shift dodge  |  C campaign' % (face, name))
            else:
                tip = ReclaimGlobals.streetPlayEntryTip(
                    zoneId, face=face, fallbackName=name)
        # Ink edge vignette on polluted ACTS enter; tip fades in as it clears.
        if self._streetIsPolluted(zoneId):
            self._playEntryVignette(zoneId, tip, tipHose=tipHose)
        else:
            self._clearVignette()
            self._showTip(tip, tipHose=tipHose)
        if act and act.get('id') == 'loopy' and act.get('approachTip'):
            self._armLoopyApproachTip(zoneId)
        if act and act.get('id') == 'finale' and act.get('approachTip'):
            self._armSillyApproachTip(zoneId)
        self.accept('r', self._requestReclaim)
        self.accept('c', self._requestCampaign)
        # Auto-field the **campaign** act (not street-pack R) so C and auto
        # share one path — no C-vs-auto-reclaim race / ~startcampaign.
        self._autoReclaimZone = zoneId
        delay = AUTO_RECLAIM_DELAY_SEC
        packId = ReclaimGlobals.streetPackId(zoneId)
        if packId == 'loopy-smudge':
            delay = LOOPY_AUTO_RECLAIM_DELAY_SEC
        elif packId == 'punchline-sludge':
            delay = PUNCHLINE_AUTO_RECLAIM_DELAY_SEC
        elif packId == 'silly-overlord':
            delay = SILLY_AUTO_RECLAIM_DELAY_SEC
        taskMgr.doMethodLater(  # noqa: F821
            delay,
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
            # Act-enter banner first (hose-pop + cream edge); tip keeps
            # stretch-punch. Early/mid trusted Oswald lead banners settle.
            act = self._actForZone(zoneId)
            banner = act.get('banner') if act else None
            trustSettle = bool(act) and not act.get('finale')
            if banner:
                self._flashBanner(
                    banner, trustSettle=trustSettle, creamEdge=True)
            else:
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
        """Kick campaign act once per street enter (prefer C over street-pack R)."""
        zoneId = self._autoReclaimZone
        if zoneId is None:
            return task.done
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or int(getattr(av, 'zoneId', -1)) != int(zoneId):
            return task.done
        if self._reclaimLive:
            return task.done
        # Campaign attach owns act unlocks / ACTS params — avoids C race.
        self._requestCampaign()
        self._flashBanner(
            ReclaimGlobals.streetAutoFlash(zoneId, face=_face()))
        return task.done

    def _sillyApproachTipTaskName(self, zoneId):
        return 'playEntrySillyApproachTip-%s' % int(zoneId)

    def _armSillyApproachTip(self, zoneId):
        """Schedule mid-act almost-confess tip after Silly Street entry."""
        self._cancelSillyApproachTip()
        act = self._actForZone(zoneId)
        if act is None or not act.get('approachTip'):
            return
        delay = float(getattr(
            CampaignGlobals, 'SILLY_APPROACH_TIP_DELAY_SEC',
            _SILLY_APPROACH_TIP_DELAY_FALLBACK_SEC))
        delay = max(0.5, delay)
        self._approachTipZone = int(zoneId)
        taskMgr.doMethodLater(  # noqa: F821
            delay,
            self._showSillyApproachTip,
            self._sillyApproachTipTaskName(zoneId))

    def _cancelSillyApproachTip(self):
        zoneId = self._approachTipZone
        self._approachTipZone = None
        if zoneId is None:
            return
        try:
            taskMgr.remove(self._sillyApproachTipTaskName(zoneId))  # noqa: F821
        except Exception:
            pass

    def _showSillyApproachTip(self, task):
        """Swap tip bar to Oswald almost-confess half-truth (mid-act)."""
        zoneId = self._approachTipZone
        self._approachTipZone = None
        if zoneId is None:
            return task.done
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or int(getattr(av, 'zoneId', -1)) != int(zoneId):
            return task.done
        act = self._actForZone(zoneId)
        if act is None or act.get('id') != 'finale':
            return task.done
        tip = act.get('approachTip')
        if not tip:
            return task.done
        # Reuse Silly tipHose — entryTipUnease keeps fracture settle +
        # cream hose settle so the almost-confess tip lands juicier.
        self._showTip(tip, tipHose='silly')
        return task.done

    def _loopyApproachTipTaskName(self, zoneId):
        return 'playEntryLoopyApproachTip-%s' % int(zoneId)

    def _armLoopyApproachTip(self, zoneId):
        """Schedule mid-act Loopy unease tip after trusted street entry."""
        self._cancelLoopyApproachTip()
        act = self._actForZone(zoneId)
        if act is None or act.get('id') != 'loopy' or not act.get('approachTip'):
            return
        delay = float(getattr(
            CampaignGlobals, 'LOOPY_APPROACH_TIP_DELAY_SEC',
            _LOOPY_APPROACH_TIP_DELAY_FALLBACK_SEC))
        delay = max(0.5, delay)
        self._loopyApproachTipZone = int(zoneId)
        taskMgr.doMethodLater(  # noqa: F821
            delay,
            self._showLoopyApproachTip,
            self._loopyApproachTipTaskName(zoneId))

    def _cancelLoopyApproachTip(self):
        zoneId = self._loopyApproachTipZone
        self._loopyApproachTipZone = None
        if zoneId is None:
            return
        try:
            taskMgr.remove(self._loopyApproachTipTaskName(zoneId))  # noqa: F821
        except Exception:
            pass

    def _showLoopyApproachTip(self, task):
        """Swap tip bar to Loopy mid-act Oswald unease (before Punchline)."""
        zoneId = self._loopyApproachTipZone
        self._loopyApproachTipZone = None
        if zoneId is None:
            return task.done
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or int(getattr(av, 'zoneId', -1)) != int(zoneId):
            return task.done
        act = self._actForZone(zoneId)
        if act is None or act.get('id') != 'loopy':
            return task.done
        tip = act.get('approachTip')
        if not tip:
            return task.done
        # tipHose='loopy' — shared tip pop + trust-fracture settle when
        # armed (no cream hose / wash deepen; Punchline owns tip cream).
        self._showTip(tip, tipHose='loopy')
        return task.done

    def _showHubTip(self):
        """TTC hub tip — Oswald points at Loopy / soft next / victory replay."""
        face = _face()
        if self._softNextCue:
            tip = self._softNextCue
        elif self._victoryEpilogue:
            tip = CampaignGlobals.hubPlayEntryTip(
                face=face,
                victory=True,
                chasePending=bool(self._chasePending))
        elif self._softNextStreet:
            tip = CampaignGlobals.hubPlayEntryTip(
                face=face, nextStreet=self._softNextStreet)
        else:
            tip = getattr(
                CampaignGlobals, 'HUB_TIP', None) or (
                CampaignGlobals.hubPlayEntryTip(face=face))
        self._showTip(tip)
        if self._victoryEpilogue and self._chasePending and not self._softNextCue:
            self._flashBanner(
                "%s's stain remains — wash the betrayal chase!" % face,
                trustSettle=True)
        elif self._victoryEpilogue and not self._softNextCue:
            self._flashBanner(
                'Campaign complete — replay from hub / C on Loopy!',
                trustSettle=True)
        else:
            self._flashBanner(
                '%s needs you — hop a tunnel and reclaim purity!' % face,
                trustSettle=True)

    def _onCampaignVictory(self, reclaimCount=0):
        # Latch victory so hub tip stops inviting Act 1 as if brand-new.
        # Chase is still pending until oswaldBetrayalChaseCleared / epilogue.
        self._victoryEpilogue = True
        self._chasePending = True

    def _onCampaignEpilogue(self, doId=0):
        """Chase-clear soft-end — hub replay tip + Loopy rematch latch."""
        if not bool(getattr(
                CampaignGlobals, 'CAMPAIGN_EPILOGUE_ENABLED', True)):
            return
        self._victoryEpilogue = True
        self._chasePending = False
        face = _face()
        tip = getattr(
            CampaignGlobals, 'CAMPAIGN_EPILOGUE_CUE', None) or (
            CampaignGlobals.hubVictoryReplayTip(face=face))
        self._latchSoftNextCue(
            tip,
            nextZone=CampaignGlobals.ACTS[0]['zoneId'],
            nextStreet=CampaignGlobals.ACTS[0]['name'])

    def _onCampaignActUnlocked(self, nextIndex=0, zoneId=0):
        """Latch unlock + refresh hub crumbs (dim locked acts → full reclaim)."""
        try:
            from toontown.safezone.CorruptStreetBreadcrumb import (
                noteCampaignActUnlocked)
            noteCampaignActUnlocked(nextIndex, zoneId)
        except Exception:
            pass

    def _mirrorCampaignActUnlocked(self, clearedZoneId, nxt):
        """Client-side campaignActUnlocked when AI messenger is process-local."""
        if nxt is None or clearedZoneId is None:
            return
        nextIndex = None
        for i, act in enumerate(CampaignGlobals.ACTS):
            if int(act['zoneId']) == int(clearedZoneId):
                nextIndex = i + 1
                break
        if nextIndex is None or nextIndex >= len(CampaignGlobals.ACTS):
            return
        nextZone = int(nxt.get('zoneId', 0) or 0)
        # Prefer messenger so CorruptStreetBreadcrumb.accept also fires;
        # fall back to direct latch if messenger is unavailable.
        try:
            messenger.send(  # noqa: F821
                'campaignActUnlocked', [nextIndex, nextZone])
        except Exception:
            self._onCampaignActUnlocked(nextIndex, nextZone)

    def _onReclaimStart(self, *args):
        self._reclaimLive = True
        self._cancelAutoReclaim()
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        zoneId = getattr(av, 'zoneId', None) if av is not None else None
        if av is not None and hasattr(av, 'enableHackSlashMelee'):
            try:
                av.enableHackSlashMelee(spawnHostiles=False)
            except Exception:
                pass
        self._flashBanner(
            ReclaimGlobals.streetReclaimLiveFlash(zoneId, face=_face()))

    def _onReclaimFailed(self, zoneId=None):
        """KO fail plate — drop live latch so R / re-enter can retry reclaim.

        Without this, `_requestReclaim` / auto-start early-return until a
        hub hop clears `_reclaimLive` via zone change. No CampaignDirectorAI
        edits — director already broadcasts announceReclaimFailed.
        """
        self._reclaimLive = False
        face = _face()
        tip = getattr(ReclaimGlobals, 'BANNER_FAILED_RETRY_TIP', None)
        if tip:
            try:
                tip = tip % face if '%s' in tip else tip
            except Exception:
                tip = (
                    '%s: reclaim failed — press R or re-enter to retry  |  '
                    'F fight  |  C campaign' % face)
        else:
            tip = (
                '%s: reclaim failed — press R or re-enter to retry  |  '
                'F fight  |  C campaign' % face)
        self._showTip(tip)

    def _latchSoftNextCue(self, tip, nextZone=None, nextStreet=None):
        """Persist next-street tip across hub / playground zone changes."""
        lined = '%s  |  F fight  |  C campaign' % tip
        self._softNextCue = lined
        if nextZone is not None:
            self._softNextZone = int(nextZone)
        if nextStreet:
            self._softNextStreet = nextStreet
        self._showTip(lined)

    def _onPurity(self, zoneId):
        """Yield the celebration banner to CampaignHandoff; tip shows next street."""
        self._reclaimLive = False
        act, nxt = self._actsAroundZone(zoneId)
        face = _face()
        if act and act.get('finale'):
            tip = act.get('nextCue') or (
                getattr(CampaignGlobals, 'FINALE_TWIST_TEASE', None)
                or "%s's smile feels… wrong" % face)
            # Rematch soft cue — hub points back at Loopy without ~startcampaign.
            self._latchSoftNextCue(
                tip,
                nextZone=CampaignGlobals.ACTS[0]['zoneId'],
                nextStreet=CampaignGlobals.ACTS[0]['name'])
            return
        # Mid-act clear unlocks the next ACTS index — mirror AI send for crumbs.
        self._mirrorCampaignActUnlocked(zoneId, nxt)
        if act and act.get('nextCue'):
            tip = act['nextCue']
        elif nxt is not None:
            tip = '%s points the tunnel → %s' % (
                face, nxt.get('name', 'the next street'))
        else:
            tip = '%s cheers — purity holds!' % face
        nextZone = nxt['zoneId'] if nxt is not None else None
        nextStreet = (
            (act.get('nextStreet') if act else None)
            or (nxt.get('name') if nxt is not None else None))
        # Persist next-street / twist cue on the tip bar (survives hub hops).
        self._latchSoftNextCue(tip, nextZone=nextZone, nextStreet=nextStreet)

    def _onHandoffCue(self, nextStreet=None, cueText=None):
        """Latch CampaignHandoff's next-street beat onto the tip bar."""
        text = cueText
        if not text and nextStreet:
            text = '%s points the way → %s' % (_face(), nextStreet)
        if not text:
            return
        nextZone = None
        streetName = nextStreet
        if streetName:
            for act in CampaignGlobals.ACTS:
                if act.get('name') == streetName:
                    nextZone = act.get('zoneId')
                    break
        self._latchSoftNextCue(text, nextZone=nextZone, nextStreet=streetName)

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
        # Cancel pending auto-campaign so R and auto don't double-fire.
        self._cancelAutoReclaim()
        if self._reclaimLive:
            return
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return
        pm.d_requestStreetEvent(0)
        self._flashBanner('%s is calling street reclaim…' % _face())

    def _requestCampaign(self):
        # Cancel pending auto so C wins cleanly (no street-pack race).
        self._cancelAutoReclaim()
        # Replay from victory clears the epilogue hub tip for the new run.
        if self._victoryEpilogue:
            self._victoryEpilogue = False
            self._chasePending = False
            self._softNextCue = None
            self._softNextZone = None
            self._softNextStreet = None
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return
        pm.d_requestStreetEvent(1)
        self._flashBanner('%s is calling the next act…' % _face())

    def _playEntryVignette(self, zoneId, tipText, tipHose=None):
        """Brief ink edge darken that fades as the tip bar appears."""
        self._clearVignette()
        root = self._buildVignetteRoot(zoneId)
        if root is None:
            self._showTip(tipText, tipHose=tipHose)
            return
        self._vignetteRoot = root
        # Tip starts invisible, fades in while vignette holds/fades out.
        self._showTip(tipText, fadeIn=True, tipHose=tipHose)
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
            # Fade + hose pop land together after the ink edge holds.
            tipParts = [
                LerpColorScaleInterval(tipNP, tipFade, Vec4(1, 1, 1, 1)),
            ]
            hose = self._tipHosePopInterval(tipNP, tipHose=tipHose)
            if hose is not None:
                tipParts.append(hose)
            # Arm tip cream wash when hose starts (not at vignette t=0)
            # so DELAY_SEC tracks hose settle like clean path.
            tipLand = [Parallel(*tipParts)]
            if tipHose == 'punchline':
                tipLand.append(Func(self._armPunchlineTipCreamWash))
            elif tipHose == 'silly':
                tipLand.append(Func(self._armSillyTipCreamWash))
            parts.append(Sequence(
                Wait(tipDelay),
                Parallel(*tipLand),
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

    def _showTip(self, text, fadeIn=False, tipHose=None):
        self._clearTip()
        tn = TextNode('play-entry-tip')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 0.95, 0.55, 1)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        settle = float(CampaignGlobals.PLAY_ENTRY_TIP_SCALE)
        tipPos = CampaignGlobals.PLAY_ENTRY_TIP_POS
        np.setScale(settle)
        np.setPos(float(tipPos[0]), float(tipPos[1]), float(tipPos[2]))
        if fadeIn:
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColorScale(1, 1, 1, 0)
        self._tipNP = np
        # Immediate pop for clean-street / handoff tips; vignette path
        # starts the hose sequence with the tip fade instead.
        if not fadeIn:
            self._playTipHosePop(np, tipHose=tipHose)

    def _tipHosePopInterval(self, tipNP, tipHose=None):
        """Build flat squash → tall stretch → settle Sequence (does not start).

        tipHose='loopy' uses the shared PLAY_ENTRY tip pop plus Oswald
        trust-fracture settle when Loopy carries trustFracture — mid-act
        unease approach tip before Punchline handoff (no cream hose /
        wash deepen). tipHose='punchline' uses Act 2 Punchline tunables +
        Oswald-trust settle bounce. When the Punchline act carries
        trustFracture (#190 deepen), settle holds a rubbery beat longer
        (unease tip), then a deepened cream hose settle past #256
        (juicier overshoot → rest → micro rebound) so the Act 2 unease
        tip lands rubber-hose and reads juicier. tipHose='silly' uses
        Act 3 Silly Overlord tunables + trust settle; when the finale
        act carries entryTipUnease, settle holds the longer fracture beat
        (entry foreshadow + mid-act almost-confess approach tip — no
        twist spoil), then a juicier cream hose settle past #279 so the
        trust-fracture tip lands rubber-hose and clear (taller/longer
        primary overshoot; no tip rebound — Punchline deepen owns that;
        distinct from #251/#279 wash aftershock and betrayal banner
        #288). Default path keeps the shared PLAY_ENTRY_TIP_* hose pop.
        """
        if tipNP is None:
            return None
        try:
            if tipNP.isEmpty():
                return None
        except Exception:
            return None
        settle = float(CampaignGlobals.PLAY_ENTRY_TIP_SCALE)
        trustOvershootAttr = None
        trustRestAttr = None
        creamHoseSettle = False
        creamHoseOvershootAttr = None
        creamHoseRestAttr = None
        creamHoseReboundAttr = None
        creamHoseReboundRestAttr = None
        if tipHose == 'loopy':
            sx, sy, sz, squashSec = CampaignGlobals.PLAY_ENTRY_TIP_POP_SQUASH
            tx, ty, tz, stretchSec = CampaignGlobals.PLAY_ENTRY_TIP_POP_STRETCH
            settleSec = float(CampaignGlobals.PLAY_ENTRY_TIP_POP_SETTLE_SEC)
            trustSettle = True
            # Loopy mid-act unease tip: longer fracture settle when armed.
            loopyAct = None
            for act in getattr(CampaignGlobals, 'ACTS', ()):
                if act.get('id') == 'loopy':
                    loopyAct = act
                    break
            if loopyAct is not None and loopyAct.get('trustFracture'):
                trustOvershootAttr = 'OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT'
                trustRestAttr = 'OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC'
            else:
                trustOvershootAttr = 'OSWALD_TRUST_BANNER_SETTLE_OVERSHOOT'
                trustRestAttr = 'OSWALD_TRUST_BANNER_SETTLE_REST_SEC'
        elif tipHose == 'punchline':
            sx, sy, sz, squashSec = getattr(
                CampaignGlobals, 'PUNCHLINE_ACT_TIP_POP_SQUASH',
                CampaignGlobals.PLAY_ENTRY_TIP_POP_SQUASH)
            tx, ty, tz, stretchSec = getattr(
                CampaignGlobals, 'PUNCHLINE_ACT_TIP_POP_STRETCH',
                CampaignGlobals.PLAY_ENTRY_TIP_POP_STRETCH)
            settleSec = float(getattr(
                CampaignGlobals, 'PUNCHLINE_ACT_TIP_POP_SETTLE_SEC',
                CampaignGlobals.PLAY_ENTRY_TIP_POP_SETTLE_SEC))
            trustSettle = True
            # Punchline unease tip: longer fracture settle when armed.
            punchAct = None
            for act in getattr(CampaignGlobals, 'ACTS', ()):
                if act.get('id') == 'punchline':
                    punchAct = act
                    break
            if punchAct is not None and punchAct.get('trustFracture'):
                trustOvershootAttr = 'OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT'
                trustRestAttr = 'OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC'
            else:
                trustOvershootAttr = 'PUNCHLINE_ACT_TIP_TRUST_SETTLE_OVERSHOOT'
                trustRestAttr = 'PUNCHLINE_ACT_TIP_TRUST_SETTLE_REST_SEC'
            # Deepened cream hose settle after trust/fracture bounce
            # (#198 / #227 / #256 deepen) — juicier overshoot → rest →
            # micro rebound past #256.
            creamHoseSettle = bool(getattr(
                CampaignGlobals,
                'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', True))
            if creamHoseSettle:
                creamHoseOvershootAttr = (
                    'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT')
                creamHoseRestAttr = (
                    'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC')
                creamHoseReboundAttr = (
                    'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND')
                creamHoseReboundRestAttr = (
                    'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND_REST_SEC')
        elif tipHose == 'silly':
            sx, sy, sz, squashSec = getattr(
                CampaignGlobals, 'SILLY_ACT_TIP_POP_SQUASH',
                CampaignGlobals.PLAY_ENTRY_TIP_POP_SQUASH)
            tx, ty, tz, stretchSec = getattr(
                CampaignGlobals, 'SILLY_ACT_TIP_POP_STRETCH',
                CampaignGlobals.PLAY_ENTRY_TIP_POP_STRETCH)
            settleSec = float(getattr(
                CampaignGlobals, 'SILLY_ACT_TIP_POP_SETTLE_SEC',
                CampaignGlobals.PLAY_ENTRY_TIP_POP_SETTLE_SEC))
            trustSettle = True
            # Silly Overlord entry unease: longer fracture settle when armed.
            # Tip-only — finale must not set trustFracture (victory sunny).
            sillyAct = None
            for act in getattr(CampaignGlobals, 'ACTS', ()):
                if act.get('id') == 'finale':
                    sillyAct = act
                    break
            if sillyAct is not None and sillyAct.get('entryTipUnease'):
                trustOvershootAttr = 'OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT'
                trustRestAttr = 'OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC'
            else:
                trustOvershootAttr = 'SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT'
                trustRestAttr = 'SILLY_ACT_TIP_TRUST_SETTLE_REST_SEC'
            # Deepened cream hose settle after fracture bounce (#207 / #232 /
            # #279). Taller/longer primary overshoot only — no tip rebound
            # (Punchline deepen owns that micro bounce; wash aftershock
            # deepen past #279 rides tipHose='silly' beside this settle).
            creamHoseSettle = bool(getattr(
                CampaignGlobals,
                'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', True))
            if creamHoseSettle:
                creamHoseOvershootAttr = (
                    'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT')
                creamHoseRestAttr = (
                    'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC')
        else:
            sx, sy, sz, squashSec = CampaignGlobals.PLAY_ENTRY_TIP_POP_SQUASH
            tx, ty, tz, stretchSec = CampaignGlobals.PLAY_ENTRY_TIP_POP_STRETCH
            settleSec = float(CampaignGlobals.PLAY_ENTRY_TIP_POP_SETTLE_SEC)
            trustSettle = False
        settlePt = Point3(settle, settle, settle)
        squashPt = Point3(settle * sx, settle * sy, settle * sz)
        stretchPt = Point3(settle * tx, settle * ty, settle * tz)
        try:
            tipNP.setScale(settlePt)
        except Exception:
            return None
        parts = [
            LerpScaleInterval(
                tipNP, float(squashSec), squashPt, blendType='easeOut'),
            LerpScaleInterval(
                tipNP, float(stretchSec), stretchPt, blendType='easeOut'),
            LerpScaleInterval(
                tipNP, settleSec, settlePt, blendType='easeIn'),
        ]
        if trustSettle:
            ox, oy, oz, overSec = getattr(
                CampaignGlobals, trustOvershootAttr,
                getattr(
                    CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_OVERSHOOT',
                    (0.90, 1.0, 1.14, 0.07)))
            restSec = float(getattr(
                CampaignGlobals, trustRestAttr,
                getattr(
                    CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_REST_SEC',
                    0.09)))
            overPt = Point3(settle * ox, settle * oy, settle * oz)
            parts.append(LerpScaleInterval(
                tipNP, float(overSec), overPt, blendType='easeOut'))
            parts.append(LerpScaleInterval(
                tipNP, restSec, settlePt, blendType='easeIn'))
        if creamHoseSettle and creamHoseOvershootAttr:
            creamOver = getattr(
                CampaignGlobals, creamHoseOvershootAttr, None)
            cx = cy = cz = creamOverSec = None
            if creamOver:
                try:
                    cx, cy, cz, creamOverSec = creamOver
                    creamOverSec = float(creamOverSec)
                except Exception:
                    creamOverSec = None
            if creamOverSec is not None and creamOverSec > 0.0:
                creamRestSec = float(getattr(
                    CampaignGlobals, creamHoseRestAttr, 0.09))
                creamOverPt = Point3(
                    settle * float(cx), settle * float(cy), settle * float(cz))
                parts.append(LerpScaleInterval(
                    tipNP, max(0.01, creamOverSec), creamOverPt,
                    blendType='easeOut'))
                parts.append(LerpScaleInterval(
                    tipNP, max(0.01, creamRestSec), settlePt,
                    blendType='easeIn'))
                # Optional micro rebound — Punchline tip cream hose deepen
                # past #256.
                if creamHoseReboundAttr:
                    creamRebound = getattr(
                        CampaignGlobals, creamHoseReboundAttr, None)
                    rx = ry = rz = reboundSec = None
                    if creamRebound:
                        try:
                            rx, ry, rz, reboundSec = creamRebound
                            reboundSec = float(reboundSec)
                        except Exception:
                            reboundSec = None
                    if reboundSec is not None and reboundSec > 0.0:
                        reboundRestSec = float(getattr(
                            CampaignGlobals, creamHoseReboundRestAttr, 0.06))
                        reboundPt = Point3(
                            settle * float(rx), settle * float(ry),
                            settle * float(rz))
                        parts.append(LerpScaleInterval(
                            tipNP, max(0.01, reboundSec), reboundPt,
                            blendType='easeOut'))
                        parts.append(LerpScaleInterval(
                            tipNP, max(0.01, reboundRestSec), settlePt,
                            blendType='easeIn'))
        return Sequence(*parts, name='playEntryTipHosePop')

    def _armPunchlineTipCreamWash(self):
        """Soft cream wash after Punchline tip hose (#91) — tip path only."""
        try:
            from toontown.campaign.PunchlineTipCreamWashFx import (
                playPunchlineTipCreamWash)
            playPunchlineTipCreamWash()
        except Exception:
            pass

    def _armSillyTipCreamWash(self):
        """Deepened cream wash + aftershock after Silly tip (#95 / #251)."""
        try:
            from toontown.campaign.SillyTipCreamWashFx import (
                playSillyTipCreamWash)
            playSillyTipCreamWash()
        except Exception:
            pass

    def _playTipHosePop(self, tipNP, tipHose=None):
        """Short rubber-hose scale pop when the street-entry tip lands.

        Punchline Act 2 tipHose appends a deepened cream hose settle past
        #256 (overshoot → rest → micro rebound) after the trust/fracture
        bounce, then arms a delayed soft cream wash pulse. Silly Act 3
        tipHose appends a juicier cream hose settle after the fracture
        bounce (almost-confess / trust-fracture tip; no tip rebound),
        then arms the cream wash (act-banner / trust wash twin) under
        the tip bar.
        """
        if self._tipIval:
            try:
                self._tipIval.pause()
            except Exception:
                pass
            self._tipIval = None
        ival = self._tipHosePopInterval(tipNP, tipHose=tipHose)
        if ival is None:
            return
        self._tipIval = ival
        self._tipIval.start()
        if tipHose == 'punchline':
            self._armPunchlineTipCreamWash()
        elif tipHose == 'silly':
            self._armSillyTipCreamWash()

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
        try:
            from toontown.campaign.PunchlineTipCreamWashFx import (
                clearPunchlineTipCreamWash)
            clearPunchlineTipCreamWash()
        except Exception:
            pass
        try:
            from toontown.campaign.SillyTipCreamWashFx import (
                clearSillyTipCreamWash)
            clearSillyTipCreamWash()
        except Exception:
            pass

    def _bannerHosePopInterval(self, bannerNP, trustSettle=False):
        """Flat squash → tall stretch → settle for act-enter flash banners.

        Early/mid Oswald trusted reclaim-lead banners append a soft
        overshoot → rest settle bounce (tunables in CampaignGlobals).
        """
        if bannerNP is None:
            return None
        try:
            if bannerNP.isEmpty():
                return None
        except Exception:
            return None
        settle = float(CampaignGlobals.PLAY_ENTRY_BANNER_SCALE)
        sx, sy, sz, squashSec = CampaignGlobals.PLAY_ENTRY_BANNER_POP_SQUASH
        tx, ty, tz, stretchSec = CampaignGlobals.PLAY_ENTRY_BANNER_POP_STRETCH
        settleSec = float(CampaignGlobals.PLAY_ENTRY_BANNER_POP_SETTLE_SEC)
        settlePt = Point3(settle, settle, settle)
        squashPt = Point3(settle * sx, settle * sy, settle * sz)
        stretchPt = Point3(settle * tx, settle * ty, settle * tz)
        try:
            bannerNP.setScale(settlePt)
        except Exception:
            return None
        parts = [
            LerpScaleInterval(
                bannerNP, float(squashSec), squashPt, blendType='easeOut'),
            LerpScaleInterval(
                bannerNP, float(stretchSec), stretchPt, blendType='easeOut'),
            LerpScaleInterval(
                bannerNP, settleSec, settlePt, blendType='easeIn'),
        ]
        if trustSettle:
            ox, oy, oz, overSec = getattr(
                CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_OVERSHOOT',
                (0.90, 1.0, 1.14, 0.07))
            restSec = float(getattr(
                CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_REST_SEC', 0.09))
            overPt = Point3(settle * ox, settle * oy, settle * oz)
            parts.append(LerpScaleInterval(
                bannerNP, float(overSec), overPt, blendType='easeOut'))
            parts.append(LerpScaleInterval(
                bannerNP, restSec, settlePt, blendType='easeIn'))
        return Sequence(*parts, name='playEntryBannerHosePop')

    def _flashBanner(self, text, trustSettle=False, creamEdge=False):
        """Act-enter / reclaim cue flash with tip-matched rubber-hose pop.

        Act-enter ACTS banners (creamEdge=True) also pulse a soft cream
        edge frame + tip flecks — wave-announce cream edge twin (#87) —
        then a delayed soft cream wash pulse (trust / finale / victory
        wash twin) under the edge.
        """
        self._clearFlash()
        tn = TextNode('play-entry-flash')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 0.85, 1, 1)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.8)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        settle = float(CampaignGlobals.PLAY_ENTRY_BANNER_SCALE)
        pos = CampaignGlobals.PLAY_ENTRY_BANNER_POS
        np.setScale(settle)
        np.setPos(float(pos[0]), float(pos[1]), float(pos[2]))
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.setColorScale(1, 1, 1, 0)
        self._flashNP = np
        fadeIn = float(CampaignGlobals.PLAY_ENTRY_BANNER_FADE_IN_SEC)
        hold = float(CampaignGlobals.PLAY_ENTRY_BANNER_HOLD_SEC)
        fadeOut = float(CampaignGlobals.PLAY_ENTRY_BANNER_FADE_OUT_SEC)
        land = [LerpColorScaleInterval(np, fadeIn, Vec4(1, 1, 1, 1))]
        hose = self._bannerHosePopInterval(np, trustSettle=trustSettle)
        if hose is not None:
            land.append(hose)
        if creamEdge:
            try:
                from toontown.campaign.ActBannerCreamEdgeFx import (
                    playActBannerCreamEdge)
                playActBannerCreamEdge()
            except Exception:
                pass
            # Soft cream wash pulse after cream edge (#110) — trust /
            # finale / victory wash grammar. Act-enter only.
            try:
                from toontown.campaign.ActBannerCreamWashFx import (
                    playActBannerCreamWash)
                playActBannerCreamWash()
            except Exception:
                pass
        self._flashIval = Sequence(
            Parallel(*land),
            Wait(hold),
            LerpColorScaleInterval(np, fadeOut, Vec4(1, 1, 1, 0)),
            Func(self._clearFlash),
            name='playEntryFlashBanner',
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
        try:
            from toontown.campaign.ActBannerCreamEdgeFx import (
                clearActBannerCreamEdge)
            clearActBannerCreamEdge()
        except Exception:
            pass
        try:
            from toontown.campaign.ActBannerCreamWashFx import (
                clearActBannerCreamWash)
            clearActBannerCreamWash()
        except Exception:
            pass


_client = None


def ensurePlayEntryClient():
    global _client
    if _client is None:
        _client = PlayEntryClient()
    return _client

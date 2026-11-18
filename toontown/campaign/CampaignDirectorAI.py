"""Air-local campaign director: multi-act reclaim progression + finale phases."""

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from toontown.campaign import CampaignGlobals
from toontown.campaign import CampaignProgressSave
from toontown.campaign.HubStain import (
    clearHubStain,
    hubStainClearMsg,
    hubStainZone,
    syncHubStain,
)
from toontown.campaign.OswaldBetrayalChase import (
    chaseClearMsg,
    chaseDelaySec,
    chaseEnabled,
    chaseSpawnMsg,
    spawnCorruptOswald,
)
from toontown.reclaim import ReclaimGlobals
from toontown.reclaim.DistributedReclaimDirectorAI import DistributedReclaimDirectorAI


class CampaignDirectorAI(DirectObject):
    """Tracks act unlocks and starts reclaim directors per act zone.

    Act unlock (`unlockedThrough`) is hydrated / flushed per avatar via
    CampaignProgressSave so explore→fight→reclaim survives logout.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('CampaignDirectorAI')

    def __init__(self, air):
        DirectObject.__init__(self)
        self.air = air
        self.state = CampaignGlobals.STATE_IDLE
        self.actIndex = 0
        self.reclaimCount = 0
        self.unlockedThrough = 0
        self._activeZoneId = None
        self._finalePhase = 0
        # 1 after Corrupted Oswald chase clear (epilogue soft-end persist).
        self.chaseCleared = 0
        self._lastToonId = None
        self._hydratedToonId = None
        self._oswaldChaseDoId = None
        self._oswaldChaseTask = None
        self._oswaldChaseWatch = None
        self.accept('neighborhoodReclaimed', self.__onNeighborhoodReclaimed)

    def _progressEnabled(self):
        return bool(getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_ENABLED', True))

    def _progressPath(self):
        folder = getattr(self.air, 'dataFolder', '') or ''
        shard = getattr(self.air, 'districtId', None)
        if shard is None:
            shard = getattr(self.air, 'shard', None)
        return CampaignProgressSave.progressPath(folder, shard)

    def _hydrateFromToon(self, toon):
        """Load this toon's saved unlocks into the live director (relog)."""
        if not self._progressEnabled() or toon is None:
            return False
        avId = getattr(toon, 'doId', None)
        if avId is None:
            return False
        # Same toon already hydrated this process — keep live session state.
        if self._hydratedToonId == avId:
            return False
        # Switching avatars: flush prior live progress before loading next.
        if self._hydratedToonId is not None and self._hydratedToonId != avId:
            self._persistForAvatarId(self._hydratedToonId)
        progress = CampaignProgressSave.readAvatar(self._progressPath(), avId)
        self._hydratedToonId = avId
        if progress is None:
            # New toon / no blob — start from defaults (do not keep prior
            # avatar's live unlockedThrough on this shared director).
            progress = CampaignProgressSave.defaultProgress()
        CampaignProgressSave.applyProgressToDirector(self, progress)
        self._lastToonId = avId
        self.notify.debug(
            'hydrated campaign progress av=%s unlockedThrough=%s act=%s'
            % (avId, self.unlockedThrough, self.actIndex))
        # Victory + uncleared chase must re-field after relog / hub return;
        # persist alone does not keep the betrayal spawn alive.
        self._resumePendingOswaldBetrayalChase(toon)
        # Mirror unlock / victory / chaseCleared to the client so hub tip +
        # OswaldPresence match story state after relog (not session-only).
        self._pushProgressToClient(toon)
        # Hub stain is process-local pollution — re-apply after relog when
        # victory still has an uncleared chase (quiet: no re-whisper).
        self._syncHubStain(tell=False)
        return True

    def _persistForToon(self, toon=None):
        avId = None
        if toon is not None:
            avId = getattr(toon, 'doId', None)
        if avId is None:
            avId = self._lastToonId
        return self._persistForAvatarId(avId)

    def _persistForAvatarId(self, avId):
        """Flush unlockedThrough / act cursor for one avatar to dataFolder."""
        if not self._progressEnabled() or avId is None:
            return False
        blob = CampaignProgressSave.snapshotFromDirector(self)
        ok = CampaignProgressSave.writeAvatar(
            self._progressPath(), avId, blob)
        if ok:
            self._hydratedToonId = avId
            self.notify.debug(
                'persisted campaign progress av=%s unlockedThrough=%s'
                % (avId, blob.get('unlockedThrough')))
            # Keep an online client's hub tip / presence in sync after flush.
            toon = self.air.doId2do.get(int(avId))
            if toon is not None:
                self._pushProgressToClient(toon)
        return ok

    def _pushProgressToClient(self, toon):
        """Thin PollutionManager status push (login / hydrate / persist)."""
        if toon is None:
            return False
        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is None:
            return False
        push = getattr(pollutionMgr, 'pushCampaignProgressToAvatar', None)
        if not callable(push):
            return False
        try:
            # hydrate=False — caller already loaded / owns live director state.
            return bool(push(toon, hydrate=False))
        except Exception:
            self.notify.debug('campaign progress client push failed')
            return False

    def statusText(self):
        if self.state == CampaignGlobals.STATE_VICTORY:
            chaseNote = ''
            if chaseEnabled():
                if int(getattr(self, 'chaseCleared', 0) or 0):
                    chaseNote = (
                        ' Oswald stain washed — epilogue soft-end ready.')
                else:
                    chaseNote = ' Corrupted-Oswald chase after betrayal.'
            return (
                'Campaign VICTORY — purity restored, but Oswald caused '
                'the corruption!%s Reclaims: %s. Replay from %s / C on Loopy.'
                % (chaseNote, self.reclaimCount, CampaignGlobals.HUB_NAME))
        act = CampaignGlobals.ACTS[min(
            self.actIndex, len(CampaignGlobals.ACTS) - 1)]
        unlocked = [
            CampaignGlobals.ACTS[i]['name']
            for i in range(self.unlockedThrough + 1)
        ]
        phaseNote = ''
        if act.get('finale'):
            phaseNote = ' | finale phase %s/2' % (self._finalePhase + 1)
        return (
            'Campaign %s | act %s/%s (%s)%s | reclaims %s | '
            'unlocked: %s | hub %s'
            % (
                CampaignGlobals.STATE_NAMES.get(self.state, '?'),
                self.actIndex + 1,
                len(CampaignGlobals.ACTS),
                act['name'],
                phaseNote,
                self.reclaimCount,
                ', '.join(unlocked),
                CampaignGlobals.HUB_NAME,
            ))

    def startCampaign(self, toon):
        """Begin or resume the current unlocked act in the invoker's zone."""
        self._lastToonId = getattr(toon, 'doId', None)
        self._hydrateFromToon(toon)
        if self.state == CampaignGlobals.STATE_VICTORY:
            # Mid-victory with chase still pending: resume the betrayal
            # chase — do not wipe unlocks / chaseCleared for a replay.
            if self._resumePendingOswaldBetrayalChase(toon):
                tip = getattr(
                    CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_RESUME_MSG', None)
                if not tip:
                    tip = (
                        'Oswald betrayal chase still pending — stain wash '
                        'resumes! Clear the chase, then C on Loopy to replay.')
                return tip
            # Chase already cleared (or disabled): full replay wipe.
            self.actIndex = 0
            self.unlockedThrough = 0
            self.reclaimCount = 0
            self._finalePhase = 0
            self.chaseCleared = 0
            self._cancelOswaldBetrayalChase()
            # Force-wash hub now — state is still VICTORY until ACTIVE below,
            # so syncHubStain would otherwise re-apply the betrayal fog.
            clearHubStain(self.air)
            # Replay wipe must stick across the next relog.
            self._persistForToon(toon)

        self.state = CampaignGlobals.STATE_ACTIVE
        act = CampaignGlobals.ACTS[self.actIndex]
        zoneId = int(toon.zoneId)
        if zoneId != int(act['zoneId']):
            face = getattr(
                CampaignGlobals, 'RECLAIM_FACE',
                getattr(CampaignGlobals, 'PROTAGONIST', 'Oswald'))
            # Persist ACTIVE + current unlocks so a wrong-zone tip after
            # relog still resumes the same act cursor.
            self._persistForToon(toon)
            return (
                '%s needs you on %s — head there and the reclaim packs '
                'will field.' % (face, act['name']))
        result = self._startActReclaim(toon, act)
        self._persistForToon(toon)
        return result

    def advanceCampaign(self, toon, force=False):
        """Unlock / jump to the next act (moderator force for demos)."""
        self._lastToonId = getattr(toon, 'doId', None)
        self._hydrateFromToon(toon)
        if self.state == CampaignGlobals.STATE_VICTORY:
            tip = getattr(
                CampaignGlobals, 'HUB_VICTORY_TIP', None) or (
                'Campaign already complete. Head to %s / press C on Loopy '
                'to replay.' % CampaignGlobals.HUB_NAME)
            return tip

        nextIndex = self.actIndex + 1
        if nextIndex >= len(CampaignGlobals.ACTS):
            self.state = CampaignGlobals.STATE_VICTORY
            self._persistForToon(toon)
            return 'No further acts — campaign victory! ' + self.statusText()

        if not force and nextIndex > self.unlockedThrough:
            return (
                'Act %s is locked. Reclaim the current street first '
                '(or ~advancecampaign force).'
                % (nextIndex + 1))

        self._stopActiveReclaim()
        self.actIndex = nextIndex
        self.unlockedThrough = max(self.unlockedThrough, nextIndex)
        self._finalePhase = 0
        self.state = CampaignGlobals.STATE_ACTIVE
        self._persistForToon(toon)
        act = CampaignGlobals.ACTS[self.actIndex]
        hint = CampaignGlobals.handoffTravelHint(act)
        self._tellToon(toon, 'NEXT HOOD: %s. %s' % (act['name'], act['banner']))
        return (
            'Advanced to act %s: %s. %s %s'
            % (self.actIndex + 1, act['name'], hint, act['banner']))

    def _actParams(self, act):
        """Resolve start() kwargs, including finale phase 2 overrides."""
        params = {
            'seedPollution': act.get('seedPollution'),
            'packSize': act.get('packSize'),
            'maxPacks': act.get('maxPacks'),
            'corruptHp': act.get('corruptHp'),
            'corruptName': act.get('corruptName'),
            'bruteFraction': act.get('bruteFraction'),
            'bruteWaveStart': act.get('bruteWaveStart'),
            'bruteName': act.get('bruteName'),
            'snareFraction': act.get('snareFraction'),
            'snareWaveStart': act.get('snareWaveStart'),
            'snareName': act.get('snareName'),
            'gagsterFraction': act.get('gagsterFraction'),
            'gagsterWaveStart': act.get('gagsterWaveStart'),
            'gagsterName': act.get('gagsterName'),
            'waveScripts': act.get('waveScripts'),
            'banner': act.get('banner'),
            'finalePhase': 0,
            'transitionSting': False,
            'addCount': None,
            'addWaveStart': None,
            'addHp': None,
            'addName': None,
        }
        if act.get('finale'):
            if self._finalePhase >= 1:
                phase2 = act.get('phase2') or {}
                params.update(phase2)
                params['finalePhase'] = int(phase2.get('finalePhase', 2))
                params['transitionSting'] = bool(
                    phase2.get('transitionSting', True))
            else:
                params['finalePhase'] = int(act.get('finalePhase', 1))
        return params

    def _startActReclaim(self, toon, act):
        directors = getattr(self.air, 'reclaimDirectors', None)
        if directors is None:
            directors = {}
            self.air.reclaimDirectors = directors

        zoneId = int(act['zoneId'])
        existing = directors.get(zoneId)
        if existing is not None and not existing.isDeleted():
            if existing.state == ReclaimGlobals.STATE_ACTIVE:
                self._activeZoneId = zoneId
                return 'Reclaim already active for %s (zone %s).' % (
                    act['name'], zoneId)
            existing.requestDelete()
            directors.pop(zoneId, None)

        params = self._actParams(act)
        director = DistributedReclaimDirectorAI(self.air, zoneId=zoneId)
        director.generateWithRequired(zoneId)
        directors[zoneId] = director
        self._activeZoneId = zoneId
        director.start(
            zoneId,
            (toon.getX(), toon.getY(), toon.getZ()),
            toon.getH(),
            seedPollution=params.get('seedPollution'),
            packSize=params.get('packSize'),
            maxPacks=params.get('maxPacks'),
            corruptHp=params.get('corruptHp'),
            corruptName=params.get('corruptName'),
            bruteFraction=params.get('bruteFraction'),
            bruteWaveStart=params.get('bruteWaveStart'),
            bruteName=params.get('bruteName'),
            snareFraction=params.get('snareFraction'),
            snareWaveStart=params.get('snareWaveStart'),
            snareName=params.get('snareName'),
            gagsterFraction=params.get('gagsterFraction'),
            gagsterWaveStart=params.get('gagsterWaveStart'),
            gagsterName=params.get('gagsterName'),
            waveScripts=params.get('waveScripts'),
            finalePhase=params.get('finalePhase', 0),
            transitionSting=params.get('transitionSting', False),
            addCount=params.get('addCount'),
            addWaveStart=params.get('addWaveStart'),
            addHp=params.get('addHp'),
            addName=params.get('addName'))
        banner = params.get('banner') or act.get('banner')
        self._tellToon(toon, banner)
        # Player-facing attach copy — melee is auto-armed by PlayEntry.
        return (
            '%s Packs inbound on %s — press F to fight, Shift to dodge!'
            % (banner, act['name']))

    def _stopActiveReclaim(self):
        if self._activeZoneId is None:
            return
        directors = getattr(self.air, 'reclaimDirectors', None) or {}
        director = directors.get(self._activeZoneId)
        if director is not None and not director.isDeleted():
            director.stop()
            director.requestDelete()
            directors.pop(self._activeZoneId, None)
        self._activeZoneId = None

    def _tellToon(self, toon, message):
        if toon is None or not message:
            return
        try:
            if hasattr(toon, 'd_setSystemMessage'):
                toon.d_setSystemMessage(0, str(message)[:200])
            elif hasattr(toon, 'setSystemMessage'):
                toon.setSystemMessage(0, str(message)[:200])
        except Exception:
            pass

    def _toonFromLast(self):
        if self._lastToonId is None:
            return None
        return self.air.doId2do.get(self._lastToonId)

    def _pendingOswaldBetrayalChase(self):
        """True when victory landed but Corrupted Oswald chase is uncleared."""
        if self.state != CampaignGlobals.STATE_VICTORY:
            return False
        if int(getattr(self, 'chaseCleared', 0) or 0):
            return False
        return chaseEnabled()

    def _resumePendingOswaldBetrayalChase(self, toon=None):
        """Re-schedule betrayal chase after relog / hub / C mid-victory.

        Persist stores STATE_VICTORY + chaseCleared=0 across logout, but the
        chase task dies with the air process. Hydrate and startCampaign call
        this so the stain-wash fight can finish before a replay wipe.
        """
        if not self._pendingOswaldBetrayalChase():
            return False
        if toon is None:
            toon = self._toonFromLast()
        if toon is None:
            return False
        # Already scheduled or live this process — leave it alone.
        if (self._oswaldChaseTask is not None
                or self._oswaldChaseDoId is not None):
            return True
        avId = getattr(toon, 'doId', None)
        if avId is not None:
            self._lastToonId = avId
        zoneId = int(getattr(toon, 'zoneId', 0) or 0)
        if zoneId <= 0:
            # Fall back to finale street when zone is unknown.
            for act in CampaignGlobals.ACTS:
                if act.get('finale'):
                    zoneId = int(act['zoneId'])
                    break
        if zoneId <= 0 and CampaignGlobals.ACTS:
            zoneId = int(CampaignGlobals.ACTS[-1]['zoneId'])
        self._scheduleOswaldBetrayalChase(toon, zoneId)
        self.notify.info(
            'resumed pending oswald betrayal chase av=%s zone=%s'
            % (getattr(toon, 'doId', None), zoneId))
        return True

    def _syncHubStain(self, tell=False, toon=None):
        """Apply / clear TTC hub pollution from victory + chaseCleared."""
        if toon is None:
            toon = self._toonFromLast()
        whisper = None
        if tell and toon is not None:
            def whisper(msg, _toon=toon):
                self._tellToon(_toon, msg)
        wantedBefore = bool(
            self.state == CampaignGlobals.STATE_VICTORY
            and int(getattr(self, 'chaseCleared', 0) or 0) == 0)
        # Capture prior hub pollution so wash whisper only fires on a real clear.
        priorLevel = 0.0
        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is not None:
            try:
                priorLevel = float(pollutionMgr.getPollution(hubStainZone()))
            except Exception:
                priorLevel = 0.0
        wanted = syncHubStain(
            self.air,
            self.state,
            chaseCleared=int(getattr(self, 'chaseCleared', 0) or 0),
            tellToon=whisper if (tell and wantedBefore) else None)
        if tell and toon is not None and not wanted and priorLevel > 0.0:
            clearMsg = hubStainClearMsg()
            if clearMsg:
                self._tellToon(toon, clearMsg)
        return wanted

    def _cancelOswaldBetrayalChase(self):
        if self._oswaldChaseTask is not None:
            try:
                taskMgr.remove(self._oswaldChaseTask)  # noqa: F821
            except Exception:
                pass
            self._oswaldChaseTask = None
        if self._oswaldChaseWatch is not None:
            try:
                taskMgr.remove(self._oswaldChaseWatch)  # noqa: F821
            except Exception:
                pass
            self._oswaldChaseWatch = None
        doId = self._oswaldChaseDoId
        self._oswaldChaseDoId = None
        if doId is None:
            return
        corrupt = self.air.doId2do.get(doId)
        if corrupt is None:
            return
        try:
            if not corrupt.isDeleted():
                corrupt.requestDelete()
        except Exception:
            pass

    def _scheduleOswaldBetrayalChase(self, toon, zoneId):
        """After finale betrayal, field a short fightable Oswald chase."""
        self._cancelOswaldBetrayalChase()
        if not chaseEnabled():
            return
        if toon is None:
            toon = self._toonFromLast()
        if toon is None:
            return
        delay = chaseDelaySec()
        self._oswaldChaseTask = 'campaign-oswald-betrayal-chase'
        taskMgr.doMethodLater(  # noqa: F821
            delay,
            self.__spawnOswaldBetrayalChase,
            self._oswaldChaseTask,
            extraArgs=[int(getattr(toon, 'doId', 0) or 0), int(zoneId)],
            appendTask=True)

    def __spawnOswaldBetrayalChase(self, toonId, zoneId, task):
        self._oswaldChaseTask = None
        if not chaseEnabled():
            return Task.done
        toon = self.air.doId2do.get(int(toonId)) if toonId else None
        if toon is None:
            toon = self._toonFromLast()
        if toon is None:
            return Task.done
        # Prefer the toon's live zone so a hub hop still fields nearby.
        liveZone = int(getattr(toon, 'zoneId', 0) or 0) or int(zoneId)
        corrupt = spawnCorruptOswald(self.air, toon, zoneId=liveZone)
        if corrupt is None:
            return Task.done
        self._oswaldChaseDoId = getattr(corrupt, 'doId', None)
        self._tellToon(toon, chaseSpawnMsg())
        try:
            messenger.send(  # noqa: F821
                'oswaldBetrayalChase',
                [liveZone, int(self._oswaldChaseDoId or 0)])
        except Exception:
            pass
        # Watch for defeat so we can land a short clear beat.
        self._oswaldChaseWatch = 'campaign-oswald-betrayal-chase-watch'
        taskMgr.doMethodLater(  # noqa: F821
            0.5,
            self.__watchOswaldBetrayalChase,
            self._oswaldChaseWatch,
            extraArgs=[int(self._oswaldChaseDoId or 0),
                       int(getattr(toon, 'doId', 0) or 0)],
            appendTask=True)
        self.notify.info(
            'oswald betrayal chase spawned doId=%s zone=%s'
            % (self._oswaldChaseDoId, liveZone))
        return Task.done

    def __watchOswaldBetrayalChase(self, doId, toonId, task):
        if doId <= 0:
            self._oswaldChaseWatch = None
            self._oswaldChaseDoId = None
            return Task.done
        corrupt = self.air.doId2do.get(int(doId))
        alive = (
            corrupt is not None
            and not getattr(corrupt, 'isDeleted', lambda: True)()
            and not getattr(corrupt, '_defeated', False)
            and int(getattr(corrupt, 'hp', 0) or 0) > 0)
        if alive:
            return Task.again
        self._oswaldChaseWatch = None
        self._oswaldChaseDoId = None
        toon = self.air.doId2do.get(int(toonId)) if toonId else None
        if toon is None:
            toon = self._toonFromLast()
        # Persist chase-clear so relog status / epilogue know the soft-end.
        self.chaseCleared = 1
        # Wash TTC hub stain — chase copy said "wash the stain."
        self._syncHubStain(tell=True, toon=toon)
        self._persistForToon(toon)
        self._tellToon(toon, chaseClearMsg())
        if bool(getattr(CampaignGlobals, 'CAMPAIGN_EPILOGUE_ENABLED', True)):
            epiCue = getattr(
                CampaignGlobals, 'CAMPAIGN_EPILOGUE_CUE', '') or (
                'Replay from %s — C on Loopy to start over'
                % CampaignGlobals.HUB_NAME)
            self._tellToon(toon, epiCue)
        try:
            messenger.send('oswaldBetrayalChaseCleared', [int(doId)])  # noqa: F821
        except Exception:
            pass
        try:
            messenger.send('campaignEpilogue', [int(doId)])  # noqa: F821
        except Exception:
            pass
        return Task.done

    def __onNeighborhoodReclaimed(self, zoneId):
        zoneId = int(zoneId)
        if self.state != CampaignGlobals.STATE_ACTIVE:
            return
        act = CampaignGlobals.ACTS[self.actIndex]
        if zoneId != int(act['zoneId']):
            return

        self.reclaimCount += 1
        toon = self._toonFromLast()
        self.notify.info(
            'campaign reclaimed act %s zone %s (count %s phase %s)'
            % (act['id'], zoneId, self.reclaimCount, self._finalePhase))

        # Finale phase 1 → restart tougher phase 2 before victory.
        if act.get('finale') and self._finalePhase < 1:
            self._finalePhase = 1
            self._activeZoneId = None
            self._persistForToon(toon)
            phase2 = act.get('phase2') or {}
            msg = phase2.get('banner') or 'Finale Phase 2!'
            self._tellToon(toon, msg)
            if toon is not None and int(toon.zoneId) == zoneId:
                self._startActReclaim(toon, act)
            return

        handoff = act.get('handoff') or ('%s reclaimed!' % act['name'])
        if act.get('finale'):
            self.state = CampaignGlobals.STATE_VICTORY
            self._activeZoneId = None
            self._finalePhase = 0
            self._persistForToon(toon)
            self._tellToon(toon, handoff)
            messenger.send('campaignVictory', [self.reclaimCount])  # noqa: F821
            # Gameplay payload: short corrupted-Oswald chase after betrayal.
            self._scheduleOswaldBetrayalChase(toon, zoneId)
            # TTC hub fog / confront while chase pending (HubStain).
            self._syncHubStain(tell=True, toon=toon)
            return

        nextIndex = self.actIndex + 1
        if nextIndex < len(CampaignGlobals.ACTS):
            self.unlockedThrough = max(self.unlockedThrough, nextIndex)
            self.actIndex = nextIndex
            self._finalePhase = 0
            self._activeZoneId = None
            self._persistForToon(toon)
            nxt = CampaignGlobals.ACTS[nextIndex]
            # Discoverable handoff — street name only, no zone ids / magic words.
            hint = CampaignGlobals.handoffTravelHint(nxt)
            self._tellToon(toon, '%s %s' % (handoff, hint))
            messenger.send(  # noqa: F821
                'campaignActUnlocked', [nextIndex, nxt['zoneId']])
        else:
            self.state = CampaignGlobals.STATE_VICTORY
            self._activeZoneId = None
            self._syncHubStain(tell=True, toon=toon)
            self._persistForToon(toon)
            self._tellToon(toon, handoff)
            messenger.send('campaignVictory', [self.reclaimCount])  # noqa: F821


def getCampaignDirector(air):
    director = getattr(air, 'campaignDirector', None)
    if director is None:
        director = CampaignDirectorAI(air)
        air.campaignDirector = director
    return director

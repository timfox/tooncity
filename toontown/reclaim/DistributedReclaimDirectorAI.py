import math

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.DistributedCorruptToonAI import DistributedCorruptToonAI
from toontown.reclaim import ReclaimGlobals


class DistributedReclaimDirectorAI(DistributedObjectAI):
    """Owns one-street reclaim: pollution seed, escalating waves, completion."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedReclaimDirectorAI')

    def __init__(self, air, zoneId=None):
        DistributedObjectAI.__init__(self, air)
        self.reclaimZoneId = zoneId or 0
        self.state = ReclaimGlobals.STATE_IDLE
        self.pollutionHint = CorruptionGlobals.POLLUTION_PURE
        self.waveIndex = 0
        self.maxWaves = ReclaimGlobals.MAX_PACKS
        self.packAlive = 0
        self._pack = []
        self._packsSpawned = 0
        self._anchorPos = (0.0, 0.0, 0.0)
        self._anchorH = 0.0
        self._tickName = None
        self._waveDelayName = None
        self._seedPollution = ReclaimGlobals.RECLAIM_START_POLLUTION
        self._packSize = ReclaimGlobals.PACK_SIZE
        self._maxPacks = ReclaimGlobals.MAX_PACKS
        self._corruptHp = None
        self._corruptName = None
        self._bruteName = None
        self._bruteFraction = None
        self._bruteWaveStart = None
        self._snareName = None
        self._snareFraction = None
        self._snareWaveStart = None
        self._gagsterName = None
        self._gagsterFraction = None
        self._gagsterWaveStart = None
        self._waveScripts = None
        self._waveModifiers = None
        self._ambushBeats = None
        self._ambushDelayName = None
        # Cleared-wave ids that already fired their between-wave ambush.
        self._ambushDone = set()
        self._pendingAmbushWave = 0
        self._pendingAmbushScript = None
        self.finalePhase = 0
        self._transitionSting = False
        self._addCount = None
        self._addWaveStart = None
        self._addHp = None
        self._addName = None
        # Silly street mid-fight Unleash (HP fraction of maxHp); None = off.
        self._overlordP2HpFrac = None
        self._streetP2Promoted = False
        # Dedup deferred KO→contested fail while attack resolve finishes.
        self._koFailPending = False

    @staticmethod
    def startStreetPackForToon(air, toon, force=False):
        """Start STREET_PACKS reclaim with soft act-unlock gate.

        Soft-gate (story skip reduction): Punchline / Silly packs need
        campaign unlockedThrough >= their ACTS index. Loopy (act 0) stays
        open so discoverable play entry works. Hydrates CampaignProgressSave
        for the invoking toon before the gate so unlocks survive relog
        (parity with C startCampaign). When a campaign act is already live
        on this street, prefer campaign attach (C path) so R cannot race
        past unlocks. force=True bypasses the soft-gate for ~startreclaim
        demos — not a hard brick on tips / explore.

        Returns a short player-facing message (started / gated / prefer).
        """
        zoneId = int(getattr(toon, 'zoneId', 0) or 0)
        unlockedThrough = 0
        campaign = None
        try:
            from toontown.campaign import CampaignGlobals
            from toontown.campaign.CampaignDirectorAI import getCampaignDirector
            campaign = getCampaignDirector(air)
            # R soft-gate must see persisted unlocks after relog / avatar
            # switch — C already hydrates in startCampaign / advanceCampaign;
            # street-pack R must hydrate before reading unlockedThrough.
            if hasattr(campaign, '_hydrateFromToon'):
                campaign._hydrateFromToon(toon)
            unlockedThrough = int(
                getattr(campaign, 'unlockedThrough', 0) or 0)
            # Prefer campaign attach when live on this street.
            if (not force
                    and campaign.state == CampaignGlobals.STATE_ACTIVE):
                act = CampaignGlobals.ACTS[campaign.actIndex]
                if zoneId == int(act['zoneId']):
                    return campaign.startCampaign(toon)
        except Exception:
            DistributedReclaimDirectorAI.notify.warning(
                'startStreetPackForToon campaign-prefer check failed')

        if not force and not ReclaimGlobals.streetPackUnlocked(
                zoneId, unlockedThrough):
            return ReclaimGlobals.streetPackGateMessage(
                zoneId, unlockedThrough)

        directors = getattr(air, 'reclaimDirectors', None)
        if directors is None:
            directors = {}
            air.reclaimDirectors = directors
        existing = directors.get(zoneId)
        if existing is not None and not existing.isDeleted():
            if existing.state == ReclaimGlobals.STATE_ACTIVE:
                return 'Reclaim already active in zone %s.' % zoneId
            existing.requestDelete()
            directors.pop(zoneId, None)

        director = DistributedReclaimDirectorAI(air, zoneId=zoneId)
        director.generateWithRequired(zoneId)
        directors[zoneId] = director
        packKwargs = ReclaimGlobals.streetPackParams(zoneId)
        director.start(
            zoneId,
            (toon.getX(), toon.getY(), toon.getZ()),
            toon.getH(),
            **packKwargs)
        packId = ReclaimGlobals.streetPackId(zoneId)
        if packId:
            return 'Reclaim started (%s)' % packId
        return 'Reclaim packs inbound — press F to fight!'

    def getState(self):
        return self.state

    def getPollutionHint(self):
        return self.pollutionHint

    def getWaveIndex(self):
        return self.waveIndex

    def getMaxWaves(self):
        return self.maxWaves

    def getPackAlive(self):
        return self.packAlive

    def getFinalePhase(self):
        return self.finalePhase

    def b_setFinalePhase(self, phase):
        self.setFinalePhase(phase)
        self.d_setFinalePhase(phase)

    def d_setFinalePhase(self, phase):
        self.sendUpdate('setFinalePhase', [int(phase)])

    def setFinalePhase(self, phase):
        self.finalePhase = max(0, int(phase))

    def b_setState(self, state):
        self.setState(state)
        self.d_setState(state)

    def d_setState(self, state):
        self.sendUpdate('setState', [int(state)])

    def setState(self, state):
        self.state = int(state)

    def b_setPollutionHint(self, level):
        self.pollutionHint = CorruptionGlobals.clampPollution(level)
        self.sendUpdate(
            'setPollutionHint',
            [CorruptionGlobals.pollutionToNet(self.pollutionHint)])

    def b_setWaveIndex(self, waveIndex):
        self.waveIndex = max(0, int(waveIndex))
        self.sendUpdate('setWaveIndex', [self.waveIndex])

    def b_setMaxWaves(self, maxWaves):
        self.maxWaves = max(1, int(maxWaves))
        self.sendUpdate('setMaxWaves', [self.maxWaves])

    def b_setPackAlive(self, count):
        self.packAlive = max(0, int(count))
        self.sendUpdate('setPackAlive', [self.packAlive])

    def start(self, zoneId, anchorPos, anchorH=0.0,
              seedPollution=None, packSize=None, maxPacks=None,
              corruptHp=None, corruptName=None,
              bruteFraction=None, bruteWaveStart=None, bruteName=None,
              snareFraction=None, snareWaveStart=None, snareName=None,
              gagsterFraction=None, gagsterWaveStart=None, gagsterName=None,
              waveScripts=None, waveModifiers=None, ambushBeats=None,
              finalePhase=0, transitionSting=False,
              addCount=None, addWaveStart=None, addHp=None, addName=None,
              overlordP2HpFrac=None):
        """Seed pollution and spawn the first escalating corrupt wave.

        Optional overrides support multi-act campaign difficulty,
        Sludge Brute / Balloon Snare / Gunk Gagster mix ratios, per-wave
        scripts, elite HP/damage modifiers, between-wave ambush beats, and
        Ink Overlord finale (phase combat + optional P2 adds).
        overlordP2HpFrac arms Silly-street mid-fight Rising→Unleashed
        without a campaign restart (slam kit + Smudge adds).
        """
        self.reclaimZoneId = int(zoneId)
        self._anchorPos = (
            float(anchorPos[0]), float(anchorPos[1]), float(anchorPos[2]))
        self._anchorH = float(anchorH)
        self._seedPollution = (
            ReclaimGlobals.RECLAIM_START_POLLUTION
            if seedPollution is None else float(seedPollution))
        self._packSize = (
            ReclaimGlobals.PACK_SIZE if packSize is None else int(packSize))
        self._maxPacks = (
            ReclaimGlobals.MAX_PACKS if maxPacks is None else int(maxPacks))
        self._corruptHp = None if corruptHp is None else int(corruptHp)
        self._corruptName = corruptName
        self._bruteName = bruteName
        self._bruteFraction = (
            None if bruteFraction is None else float(bruteFraction))
        self._bruteWaveStart = (
            None if bruteWaveStart is None else int(bruteWaveStart))
        self._snareName = snareName
        self._snareFraction = (
            None if snareFraction is None else float(snareFraction))
        self._snareWaveStart = (
            None if snareWaveStart is None else int(snareWaveStart))
        self._gagsterName = gagsterName
        self._gagsterFraction = (
            None if gagsterFraction is None else float(gagsterFraction))
        self._gagsterWaveStart = (
            None if gagsterWaveStart is None else int(gagsterWaveStart))
        self._waveScripts = waveScripts
        self._waveModifiers = waveModifiers
        self._ambushBeats = ambushBeats
        self._ambushDone = set()
        self._transitionSting = bool(transitionSting)
        self._addCount = None if addCount is None else int(addCount)
        self._addWaveStart = (
            None if addWaveStart is None else int(addWaveStart))
        self._addHp = None if addHp is None else int(addHp)
        self._addName = addName
        if overlordP2HpFrac is None:
            self._overlordP2HpFrac = None
        else:
            self._overlordP2HpFrac = float(overlordP2HpFrac)
        self._streetP2Promoted = False
        self._clearPack(delete=True)
        self._packsSpawned = 0
        self._cancelWaveDelay()
        self._cancelAmbushDelay()

        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is not None:
            # Clear purity lock + pause re-creep *before* seeding ink so a
            # finished-reclaim lock cannot refuse the start pollution rise.
            if hasattr(pollutionMgr, 'markStreetReclaiming'):
                pollutionMgr.markStreetReclaiming(self.reclaimZoneId)
            pollutionMgr.setPollution(
                self.reclaimZoneId, self._seedPollution)

        self.b_setFinalePhase(finalePhase or 0)
        self.b_setMaxWaves(self._maxPacks)
        self.b_setWaveIndex(0)
        self.b_setPackAlive(0)
        self.b_setState(ReclaimGlobals.STATE_ACTIVE)
        self._syncPollutionHint()
        self.sendUpdate('announceReclaimStart', [])
        if self.finalePhase >= 2 and self._transitionSting:
            self.sendUpdate('announceFinalePhaseTransition', [self.finalePhase])
        self._spawnPack()

        if self._tickName is None:
            self._tickName = self.uniqueName('reclaim-tick')
            taskMgr.doMethodLater(0.5, self.__tick, self._tickName)

        self.accept('pollutionReclaimed', self.__onPollutionReclaimed)
        self._koFailPending = False
        return True

    def failStreetOnKnockout(self, avId=None):
        """Active reclaim fails when a fighter goes sad — street contested.

        Smallest authored lose beat for explore→fight→reclaim: same contested
        outcome as mid-reclaim bail (~stopreclaim), plus announceReclaimFailed
        so the client reads KO as failure (not a silent end). Defers teardown
        one tick so the corrupt attack resolve that caused the KO can finish.
        """
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return False
        if getattr(self, '_koFailPending', False):
            return False
        if avId is not None:
            av = self.air.doId2do.get(int(avId))
            if av is not None:
                avZone = int(getattr(av, 'zoneId', 0) or 0)
                if avZone and avZone != int(self.reclaimZoneId):
                    return False
        self._koFailPending = True
        try:
            self.sendUpdate('announceReclaimFailed', [])
        except Exception:
            self.notify.debug('announceReclaimFailed send failed')
        # Defer stop/delete so current CorruptToonAI hit resolve can return.
        taskMgr.doMethodLater(  # noqa: F821
            0.05,
            self.__deferredKnockoutFail,
            self.uniqueName('reclaim-ko-fail'))
        return True

    def __deferredKnockoutFail(self, task):
        """Contested bail-out after KO announce (mirrors ~stopreclaim)."""
        self._koFailPending = False
        if self.isDeleted():
            return Task.done
        zoneId = self.reclaimZoneId
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.stop()
        try:
            if not self.isDeleted():
                self.requestDelete()
        except Exception:
            pass
        directors = getattr(self.air, 'reclaimDirectors', None)
        if isinstance(directors, dict):
            directors.pop(zoneId, None)
        return Task.done

    def stop(self):
        # Bail-out while ACTIVE leaves the street contested so residual ink
        # can slowly re-creep. COMPLETE → IDLE keeps the secured mark.
        # Player KO uses the same contested path via failStreetOnKnockout.
        wasActive = self.state == ReclaimGlobals.STATE_ACTIVE
        contestedZoneId = self.reclaimZoneId
        self.ignore('pollutionReclaimed')
        self._cancelWaveDelay()
        self._cancelAmbushDelay()
        if self._tickName is not None:
            taskMgr.remove(self._tickName)
            self._tickName = None
        koTask = self.uniqueName('reclaim-ko-fail')
        try:
            taskMgr.remove(koTask)  # noqa: F821
        except Exception:
            pass
        self._koFailPending = False
        self._clearPack(delete=True)
        self.b_setPackAlive(0)
        self.b_setWaveIndex(0)
        self.b_setFinalePhase(0)
        self._transitionSting = False
        self._waveScripts = None
        self._waveModifiers = None
        self._ambushBeats = None
        self._ambushDone = set()
        self._pendingAmbushWave = 0
        self._pendingAmbushScript = None
        self._addCount = None
        self._addWaveStart = None
        self._addHp = None
        self._addName = None
        self._overlordP2HpFrac = None
        self._streetP2Promoted = False
        self.b_setState(ReclaimGlobals.STATE_IDLE)
        self.b_setPollutionHint(CorruptionGlobals.POLLUTION_PURE)
        if wasActive:
            pollutionMgr = getattr(self.air, 'pollutionManager', None)
            if pollutionMgr is not None and hasattr(
                    pollutionMgr, 'markStreetContested'):
                pollutionMgr.markStreetContested(contestedZoneId)

    def delete(self):
        self.stop()
        directors = getattr(self.air, 'reclaimDirectors', None)
        if isinstance(directors, dict):
            directors.pop(self.reclaimZoneId, None)
        DistributedObjectAI.delete(self)

    def __tick(self, task):
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return Task.done

        self._prunePack()
        self._maybePromoteStreetOverlordP2()
        self._syncPollutionHint()
        self.b_setPackAlive(len(self._pack))

        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        level = (
            pollutionMgr.getPollution(self.reclaimZoneId)
            if pollutionMgr is not None else CorruptionGlobals.POLLUTION_PURE)

        if level <= CorruptionGlobals.POLLUTION_PURE:
            self.__complete()
            return Task.done

        if (not self._pack
                and self._packsSpawned < self._maxPacks
                and self._waveDelayName is None
                and self._ambushDelayName is None):
            clearedWave = self._packsSpawned
            # Real wave clear: announce + optional ambush. Ambush clear:
            # skip re-announce (clearedWave already in _ambushDone) and
            # advance to the next scripted pack.
            if clearedWave > 0 and clearedWave not in self._ambushDone:
                self.sendUpdate('announceWaveCleared', [int(clearedWave)])
                if self._scheduleAmbushIfNeeded(clearedWave):
                    return Task.again
            self._scheduleNextWave()

        return Task.again

    def __onPollutionReclaimed(self, zoneId):
        if int(zoneId) != int(self.reclaimZoneId):
            return
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__complete()

    def __complete(self):
        if self.state == ReclaimGlobals.STATE_COMPLETE:
            return
        self._cancelWaveDelay()
        self._clearPack(delete=True)
        if self._tickName is not None:
            taskMgr.remove(self._tickName)
            self._tickName = None
        self.ignore('pollutionReclaimed')
        self.b_setPackAlive(0)
        self.b_setPollutionHint(CorruptionGlobals.POLLUTION_PURE)
        self.b_setState(ReclaimGlobals.STATE_COMPLETE)
        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is not None and hasattr(
                pollutionMgr, 'markStreetSecured'):
            pollutionMgr.markStreetSecured(self.reclaimZoneId)
        self.sendUpdate('announceReclaimComplete', [])
        # Campaign act unlock / reclaimCount / victory (slice 4 hooks).
        messenger.send('neighborhoodReclaimed', [self.reclaimZoneId])
        # Slice reward beyond CampaignPower COMBO_DAMAGE bump: jellybeans
        # + laff toon-up + street-trophy whisper (R and C paths).
        self._awardStreetClearRewards()

    def _awardStreetClearRewards(self):
        """Grant Open Toontown street-clear beans/laff to toons on this street.

        Runs after neighborhoodReclaimed so active campaign reclaimCount
        already includes this clear. Discoverable R (idle campaign) still
        awards the base jellybean / laff slice.
        """
        try:
            from toontown.campaign.CampaignPower import awardStreetClearReward
            from toontown.toon.DistributedToonAI import DistributedToonAI
        except Exception:
            self.notify.debug('street-clear reward import failed')
            return
        reclaimCount = 1
        try:
            from toontown.campaign.CampaignDirectorAI import getCampaignDirector
            campaign = getCampaignDirector(self.air)
            reclaimCount = max(
                1, int(getattr(campaign, 'reclaimCount', 0) or 0))
        except Exception:
            pass
        zoneId = int(self.reclaimZoneId or 0)
        for obj in list(self.air.doId2do.values()):
            if not isinstance(obj, DistributedToonAI):
                continue
            if int(getattr(obj, 'zoneId', 0) or 0) != zoneId:
                continue
            # Skip sad toons — KO fail already contested the street.
            if int(getattr(obj, 'hp', 1) or 0) <= 0:
                continue
            try:
                awardStreetClearReward(
                    obj, reclaimCount=reclaimCount, zoneId=zoneId)
            except Exception:
                self.notify.debug(
                    'street-clear reward failed for av %s'
                    % getattr(obj, 'doId', '?'))

    def _syncPollutionHint(self):
        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is None:
            return
        self.b_setPollutionHint(pollutionMgr.getPollution(self.reclaimZoneId))

    def _prunePack(self):
        alive = []
        for corrupt in self._pack:
            if corrupt is None or corrupt.isDeleted():
                continue
            if getattr(corrupt, '_defeated', False):
                continue
            if getattr(corrupt, 'hp', 0) <= 0:
                continue
            alive.append(corrupt)
        self._pack = alive

    def _clearPack(self, delete=False):
        if delete:
            for corrupt in list(self._pack):
                try:
                    if corrupt is not None and not corrupt.isDeleted():
                        corrupt.requestDelete()
                except Exception:
                    pass
        self._pack = []
        self.packAlive = 0

    def _cancelWaveDelay(self):
        if self._waveDelayName is not None:
            taskMgr.remove(self._waveDelayName)
            self._waveDelayName = None

    def _cancelAmbushDelay(self):
        if self._ambushDelayName is not None:
            taskMgr.remove(self._ambushDelayName)
            self._ambushDelayName = None

    def _scheduleAmbushIfNeeded(self, clearedWave):
        """Schedule a between-wave ambush after clearedWave, or return False."""
        wave = int(clearedWave)
        if wave <= 0 or wave in self._ambushDone:
            return False
        script = ReclaimGlobals.resolveAmbushBeat(self._ambushBeats, wave)
        if not script:
            return False
        self._cancelAmbushDelay()
        self._ambushDelayName = self.uniqueName('reclaim-ambush-delay')
        # Capture script on the task via closure attrs.
        self._pendingAmbushWave = wave
        self._pendingAmbushScript = script
        taskMgr.doMethodLater(
            ReclaimGlobals.AMBUSH_DELAY,
            self.__spawnDelayedAmbush,
            self._ambushDelayName)
        return True

    def __spawnDelayedAmbush(self, task):
        self._ambushDelayName = None
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return Task.done
        self._prunePack()
        if self._pack:
            return Task.done
        clearedWave = int(getattr(self, '_pendingAmbushWave', 0) or 0)
        script = getattr(self, '_pendingAmbushScript', None)
        self._pendingAmbushWave = 0
        self._pendingAmbushScript = None
        if clearedWave <= 0 or not script:
            return Task.done
        self._spawnAmbush(clearedWave, script)
        return Task.done

    def _scheduleNextWave(self):
        """Beat between waves so escalation reads as a moment, not a respawn."""
        self._cancelWaveDelay()
        delay = ReclaimGlobals.WAVE_SPAWN_DELAY
        # After an ambush, keep a short pause so elite wave still reads.
        if self._ambushDone:
            delay = max(0.35, float(ReclaimGlobals.WAVE_SPAWN_DELAY) * 0.55)
        self._waveDelayName = self.uniqueName('reclaim-wave-delay')
        taskMgr.doMethodLater(delay, self.__spawnDelayedWave, self._waveDelayName)

    def __spawnDelayedWave(self, task):
        self._waveDelayName = None
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return Task.done
        if self._packsSpawned >= self._maxPacks:
            return Task.done
        self._prunePack()
        if self._pack:
            return Task.done
        self._spawnPack()
        return Task.done

    def _applyEliteModifiers(self, corrupt, mods):
        """Apply elite HP (already baked into maxHp) + damage buff to stats."""
        if not ReclaimGlobals.waveIsElite(mods):
            return
        stats = getattr(corrupt, '_stats', None)
        if not isinstance(stats, dict):
            return
        corrupt._stats = ReclaimGlobals.applyWaveDamageMultToStats(stats, mods)

    def _spawnAmbush(self, clearedWave, waveScript):
        """Spawn a between-wave ambush pack (does not advance wave index)."""
        wave = max(1, int(clearedWave))
        self._ambushDone.add(wave)
        count = max(1, len(waveScript))
        baseX, baseY, baseZ = self._anchorPos
        heading = self._anchorH
        rad = math.radians(heading)
        spawned = []
        for i in range(count):
            archetype = ReclaimGlobals.pickPackArchetype(
                wave, i, count, waveScript=waveScript)
            hp = ReclaimGlobals.packSlotHp(archetype, self._corruptHp, wave)
            name = ReclaimGlobals.packSlotName(
                archetype,
                smudgeName=self._corruptName,
                bruteName=self._bruteName,
                snareName=self._snareName,
                gagsterName=self._gagsterName,
                slotIndex=i,
                packCount=count)
            prefix = ReclaimGlobals.AMBUSH_NAME_PREFIX
            if not str(name).startswith(prefix):
                name = '%s%s' % (prefix, name)
            corrupt = DistributedCorruptToonAI(
                self.air, name=name, maxHp=hp, archetype=archetype,
                finalePhase=0)
            spawnBias = 0.0
            if archetype == CorruptionGlobals.ARCHETYPE_BRUTE:
                spawnBias = 2.2
            elif archetype == CorruptionGlobals.ARCHETYPE_SNARE:
                spawnBias = -1.4
            elif archetype == CorruptionGlobals.ARCHETYPE_GAGSTER:
                spawnBias = 0.6
            offset = (
                ReclaimGlobals.AMBUSH_FORWARD
                + (i * 0.15)
                + spawnBias)
            lateral = (i - (count - 1) / 2.0) * ReclaimGlobals.SPAWN_SPACING
            x = baseX - math.sin(rad) * offset - math.cos(rad) * lateral
            y = baseY + math.cos(rad) * offset - math.sin(rad) * lateral
            corrupt.setPos(x, y, baseZ)
            corrupt.setH(heading + 180.0)
            corrupt.generateWithRequired(self.reclaimZoneId)
            spawned.append(corrupt)
        self._pack.extend(spawned)
        self.b_setPackAlive(len(self._pack))
        self.sendUpdate('announceAmbushSpawn', [len(spawned), wave])
        self.notify.debug(
            'reclaim zone %s ambush after wave %s pack=%s' % (
                self.reclaimZoneId, wave, len(spawned)))

    def _spawnPack(self):
        wave = self._packsSpawned + 1
        waveScript = ReclaimGlobals.resolveWaveScript(self._waveScripts, wave)
        waveMods = ReclaimGlobals.resolveWaveModifiers(
            self._waveModifiers, wave)
        count = ReclaimGlobals.wavePackSize(
            self._packSize, wave, waveScript=waveScript)
        self._packsSpawned = wave
        self.b_setWaveIndex(wave)
        self.b_setMaxWaves(self._maxPacks)

        baseX, baseY, baseZ = self._anchorPos
        heading = self._anchorH
        rad = math.radians(heading)
        spawned = []
        bruteCount = 0
        snareCount = 0
        gagsterCount = 0
        for i in range(count):
            archetype = ReclaimGlobals.pickPackArchetype(
                wave, i, count,
                bruteFraction=self._bruteFraction,
                bruteWaveStart=self._bruteWaveStart,
                snareFraction=self._snareFraction,
                snareWaveStart=self._snareWaveStart,
                gagsterFraction=self._gagsterFraction,
                gagsterWaveStart=self._gagsterWaveStart,
                waveScript=waveScript)
            if archetype == CorruptionGlobals.ARCHETYPE_BRUTE:
                bruteCount += 1
            elif archetype == CorruptionGlobals.ARCHETYPE_SNARE:
                snareCount += 1
            elif archetype == CorruptionGlobals.ARCHETYPE_GAGSTER:
                gagsterCount += 1
            hp = ReclaimGlobals.packSlotHp(archetype, self._corruptHp, wave)
            hp = ReclaimGlobals.applyElitePackHp(hp, waveMods)
            # Finale / explicit zero-mix packs keep Overlord (or act) naming.
            mixOff = (
                (self._bruteFraction is not None
                 and float(self._bruteFraction) <= 0.0)
                and (self._snareFraction is None
                     or float(self._snareFraction) <= 0.0)
                and (self._gagsterFraction is None
                     or float(self._gagsterFraction) <= 0.0))
            if self._corruptName and mixOff:
                name = self._corruptName
                if count > 1 and i > 0:
                    name = '%s %s' % (self._corruptName, i + 1)
            else:
                name = ReclaimGlobals.packSlotName(
                    archetype,
                    smudgeName=self._corruptName,
                    bruteName=self._bruteName,
                    snareName=self._snareName,
                    gagsterName=self._gagsterName,
                    slotIndex=i,
                    packCount=count)
            name = ReclaimGlobals.applyElitePackName(name, waveMods)
            corrupt = DistributedCorruptToonAI(
                self.air, name=name, maxHp=hp, archetype=archetype,
                finalePhase=self.finalePhase if mixOff else 0)
            self._applyEliteModifiers(corrupt, waveMods)
            # Fan packs slightly farther each wave so the street fills forward.
            # Brutes sit a bit back so spit telegraph reads at mid-range;
            # Snares press forward so zip-lash reads in front of the pack;
            # Gagsters hold mid so lob puddles read between front and rear.
            spawnBias = 0.0
            if archetype == CorruptionGlobals.ARCHETYPE_BRUTE:
                spawnBias = 2.2
            elif archetype == CorruptionGlobals.ARCHETYPE_SNARE:
                spawnBias = -1.4
            elif archetype == CorruptionGlobals.ARCHETYPE_GAGSTER:
                spawnBias = 0.6
            offset = (
                ReclaimGlobals.SPAWN_FORWARD
                + (i * 0.15)
                + ((wave - 1) * 1.5)
                + spawnBias)
            lateral = (i - (count - 1) / 2.0) * ReclaimGlobals.SPAWN_SPACING
            x = baseX - math.sin(rad) * offset - math.cos(rad) * lateral
            y = baseY + math.cos(rad) * offset - math.sin(rad) * lateral
            corrupt.setPos(x, y, baseZ)
            corrupt.setH(heading + 180.0)
            corrupt.generateWithRequired(self.reclaimZoneId)
            spawned.append(corrupt)
        # P2 Unleashed: Smudge adds on later waves for arena pressure.
        addSpawned = self._spawnOverlordAdds(
            wave, heading, rad, baseX, baseY, baseZ)
        spawned.extend(addSpawned)
        self._pack.extend(spawned)
        self.b_setPackAlive(len(spawned))
        self.sendUpdate('announcePackSpawn', [len(spawned), wave])
        self.notify.debug(
            'reclaim zone %s wave #%s/%s pack=%s brutes=%s snares=%s '
            'gagsters=%s adds=%s elite=%s finalePhase=%s' % (
                self.reclaimZoneId, wave, self._maxPacks, len(spawned),
                bruteCount, snareCount, gagsterCount, len(addSpawned),
                bool(ReclaimGlobals.waveIsElite(waveMods)),
                self.finalePhase))

    def _maybePromoteStreetOverlordP2(self):
        """HP-threshold Rising→Unleashed for discoverable Silly street reclaim.

        Campaign C still owns the story P2 restart + Oswald twist; this path
        only flips combat (slam kit + Smudge adds) mid-fight.
        """
        if self._streetP2Promoted:
            return
        if int(self.finalePhase) != 1:
            return
        frac = self._overlordP2HpFrac
        if frac is None:
            return
        for corrupt in self._pack:
            if corrupt is None or corrupt.isDeleted():
                continue
            if getattr(corrupt, '_defeated', False):
                continue
            if not getattr(corrupt, '_isOverlord', lambda: False)():
                continue
            if ReclaimGlobals.overlordHpAtP2Threshold(
                    getattr(corrupt, 'hp', 0),
                    getattr(corrupt, 'maxHp', 0),
                    frac):
                self._promoteStreetOverlordP2()
                return

    def _promoteStreetOverlordP2(self):
        """Flip director + living Overlords to Unleashed and spawn Smudge adds."""
        if self._streetP2Promoted or int(self.finalePhase) >= 2:
            self._streetP2Promoted = True
            return
        self._streetP2Promoted = True
        self.b_setFinalePhase(2)
        self.sendUpdate('announceFinalePhaseTransition', [2])
        for corrupt in list(self._pack):
            if corrupt is None or corrupt.isDeleted():
                continue
            if getattr(corrupt, '_defeated', False):
                continue
            if not getattr(corrupt, '_isOverlord', lambda: False)():
                continue
            promote = getattr(corrupt, 'promoteFinalePhase', None)
            if callable(promote):
                promote(2)
            else:
                corrupt.setFinalePhase(2)
        wave = max(1, int(self._packsSpawned or self.waveIndex or 1))
        heading = float(self._anchorH)
        rad = math.radians(heading)
        baseX, baseY, baseZ = self._anchorPos
        addSpawned = self._spawnOverlordAdds(
            wave, heading, rad, baseX, baseY, baseZ)
        if addSpawned:
            self._pack.extend(addSpawned)
            self.b_setPackAlive(len(self._pack))
            self.notify.debug(
                'street Overlord HP-threshold P2 — spawned %s adds (wave %s)'
                % (len(addSpawned), wave))

    def _spawnOverlordAdds(self, wave, heading, rad, baseX, baseY, baseZ):
        """Spawn street Smudge adds beside Unleashed Overlord (P2 wave gate)."""
        if int(self.finalePhase) < 2:
            return []
        count = CorruptionGlobals.overlordP2AddCount(
            wave,
            addCount=self._addCount,
            addWaveStart=self._addWaveStart)
        if count <= 0:
            return []
        hp = (
            CorruptionGlobals.OVERLORD_P2_ADD_HP
            if self._addHp is None else int(self._addHp))
        name = self._addName or CorruptionGlobals.OVERLORD_P2_ADD_NAME
        spacing = float(CorruptionGlobals.OVERLORD_P2_ADD_SPACING)
        forward = float(CorruptionGlobals.OVERLORD_P2_ADD_FORWARD)
        spawned = []
        for i in range(count):
            addName = name if count == 1 else '%s %s' % (name, i + 1)
            corrupt = DistributedCorruptToonAI(
                self.air,
                name=addName,
                maxHp=hp,
                archetype=CorruptionGlobals.ARCHETYPE_INK,
                finalePhase=0)
            lateral = (i - (count - 1) / 2.0) * spacing
            offset = forward + ((wave - 1) * 0.8)
            x = baseX - math.sin(rad) * offset - math.cos(rad) * lateral
            y = baseY + math.cos(rad) * offset - math.sin(rad) * lateral
            corrupt.setPos(x, y, baseZ)
            corrupt.setH(heading + 180.0)
            corrupt.generateWithRequired(self.reclaimZoneId)
            spawned.append(corrupt)
        return spawned

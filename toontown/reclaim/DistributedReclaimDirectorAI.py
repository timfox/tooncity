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
        self.finalePhase = 0
        self._transitionSting = False
        self._addCount = None
        self._addWaveStart = None
        self._addHp = None
        self._addName = None
        # Silly street mid-fight Unleash (HP fraction of maxHp); None = off.
        self._overlordP2HpFrac = None
        self._streetP2Promoted = False

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
              waveScripts=None,
              finalePhase=0, transitionSting=False,
              addCount=None, addWaveStart=None, addHp=None, addName=None,
              overlordP2HpFrac=None):
        """Seed pollution and spawn the first escalating corrupt wave.

        Optional overrides support multi-act campaign difficulty,
        Sludge Brute / Balloon Snare / Gunk Gagster mix ratios, per-wave
        scripts, and Ink Overlord finale (phase combat + optional P2 adds).
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
        return True

    def stop(self):
        # Bail-out while ACTIVE leaves the street contested so residual ink
        # can slowly re-creep. COMPLETE → IDLE keeps the secured mark.
        wasActive = self.state == ReclaimGlobals.STATE_ACTIVE
        contestedZoneId = self.reclaimZoneId
        self.ignore('pollutionReclaimed')
        self._cancelWaveDelay()
        if self._tickName is not None:
            taskMgr.remove(self._tickName)
            self._tickName = None
        self._clearPack(delete=True)
        self.b_setPackAlive(0)
        self.b_setWaveIndex(0)
        self.b_setFinalePhase(0)
        self._transitionSting = False
        self._waveScripts = None
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
                and self._waveDelayName is None):
            clearedWave = self._packsSpawned
            if clearedWave > 0:
                self.sendUpdate('announceWaveCleared', [int(clearedWave)])
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
        # Minimal progression stub for slice 4 campaign hooks.
        messenger.send('neighborhoodReclaimed', [self.reclaimZoneId])

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

    def _scheduleNextWave(self):
        """Beat between waves so escalation reads as a moment, not a respawn."""
        self._cancelWaveDelay()
        delay = ReclaimGlobals.WAVE_SPAWN_DELAY
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

    def _spawnPack(self):
        wave = self._packsSpawned + 1
        waveScript = ReclaimGlobals.resolveWaveScript(self._waveScripts, wave)
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
            corrupt = DistributedCorruptToonAI(
                self.air, name=name, maxHp=hp, archetype=archetype,
                finalePhase=self.finalePhase if mixOff else 0)
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
            'gagsters=%s adds=%s finalePhase=%s' % (
                self.reclaimZoneId, wave, self._maxPacks, len(spawned),
                bruteCount, snareCount, gagsterCount, len(addSpawned),
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

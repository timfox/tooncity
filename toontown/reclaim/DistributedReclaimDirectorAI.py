import math

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.DistributedCorruptToonAI import DistributedCorruptToonAI
from toontown.reclaim import ReclaimGlobals


class DistributedReclaimDirectorAI(DistributedObjectAI):
    """Owns one-street reclaim: pollution seed, corrupt packs, completion."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedReclaimDirectorAI')

    def __init__(self, air, zoneId=None):
        DistributedObjectAI.__init__(self, air)
        self.reclaimZoneId = zoneId or 0
        self.state = ReclaimGlobals.STATE_IDLE
        self.pollutionHint = CorruptionGlobals.POLLUTION_PURE
        self._pack = []
        self._packsSpawned = 0
        self._anchorPos = (0.0, 0.0, 0.0)
        self._anchorH = 0.0
        self._tickName = None
        self._seedPollution = ReclaimGlobals.RECLAIM_START_POLLUTION
        self._packSize = ReclaimGlobals.PACK_SIZE
        self._maxPacks = ReclaimGlobals.MAX_PACKS
        self._corruptHp = None
        self._corruptName = None

    def getState(self):
        return self.state

    def getPollutionHint(self):
        return self.pollutionHint

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

    def start(self, zoneId, anchorPos, anchorH=0.0,
              seedPollution=None, packSize=None, maxPacks=None,
              corruptHp=None, corruptName=None):
        """Seed pollution and spawn the first corrupt pack.

        Optional overrides support multi-act campaign difficulty.
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
        self._clearPack(delete=True)
        self._packsSpawned = 0

        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is not None:
            pollutionMgr.setPollution(
                self.reclaimZoneId, self._seedPollution)

        self.b_setState(ReclaimGlobals.STATE_ACTIVE)
        self._syncPollutionHint()
        self.sendUpdate('announceReclaimStart', [])
        self._spawnPack()

        if self._tickName is None:
            self._tickName = self.uniqueName('reclaim-tick')
            taskMgr.doMethodLater(0.5, self.__tick, self._tickName)

        self.accept('pollutionReclaimed', self.__onPollutionReclaimed)
        return True

    def stop(self):
        self.ignore('pollutionReclaimed')
        if self._tickName is not None:
            taskMgr.remove(self._tickName)
            self._tickName = None
        self._clearPack(delete=True)
        self.b_setState(ReclaimGlobals.STATE_IDLE)
        self.b_setPollutionHint(CorruptionGlobals.POLLUTION_PURE)

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
        self._syncPollutionHint()

        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        level = (
            pollutionMgr.getPollution(self.reclaimZoneId)
            if pollutionMgr is not None else CorruptionGlobals.POLLUTION_PURE)

        if level <= CorruptionGlobals.POLLUTION_PURE:
            self.__complete()
            return Task.done

        if not self._pack and self._packsSpawned < self._maxPacks:
            self._spawnPack()

        return Task.again

    def __onPollutionReclaimed(self, zoneId):
        if int(zoneId) != int(self.reclaimZoneId):
            return
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__complete()

    def __complete(self):
        if self.state == ReclaimGlobals.STATE_COMPLETE:
            return
        self._clearPack(delete=True)
        if self._tickName is not None:
            taskMgr.remove(self._tickName)
            self._tickName = None
        self.ignore('pollutionReclaimed')
        self.b_setPollutionHint(CorruptionGlobals.POLLUTION_PURE)
        self.b_setState(ReclaimGlobals.STATE_COMPLETE)
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

    def _spawnPack(self):
        count = max(1, int(self._packSize))
        self._packsSpawned += 1
        baseX, baseY, baseZ = self._anchorPos
        heading = self._anchorH
        rad = math.radians(heading)
        spawned = []
        for i in range(count):
            name = self._corruptName
            if name and count > 1 and i > 0:
                name = '%s %s' % (self._corruptName, i + 1)
            corrupt = DistributedCorruptToonAI(
                self.air, name=name, maxHp=self._corruptHp)
            offset = ReclaimGlobals.SPAWN_FORWARD + (i * 0.15)
            lateral = (i - (count - 1) / 2.0) * ReclaimGlobals.SPAWN_SPACING
            x = baseX - math.sin(rad) * offset - math.cos(rad) * lateral
            y = baseY + math.cos(rad) * offset - math.sin(rad) * lateral
            corrupt.setPos(x, y, baseZ)
            corrupt.setH(heading + 180.0)
            corrupt.generateWithRequired(self.reclaimZoneId)
            spawned.append(corrupt)
        self._pack.extend(spawned)
        self.sendUpdate('announcePackSpawn', [len(spawned)])
        self.notify.debug(
            'reclaim zone %s spawned pack #%s (%s)' % (
                self.reclaimZoneId, self._packsSpawned, len(spawned)))

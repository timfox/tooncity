from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.HackSlashTarget import HackSlashTarget


class DistributedCorruptToonAI(DistributedNodeAI, HackSlashTarget):
    """AI stub for a corrupt toon enemy; defeat lowers zone pollution."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCorruptToonAI')

    def __init__(self, air, name=None, maxHp=None):
        DistributedNodeAI.__init__(self, air)
        self.name = name or CorruptionGlobals.CORRUPT_TOON_DEFAULT_NAME
        self.maxHp = maxHp if maxHp is not None else CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
        self.hp = self.maxHp
        self._defeated = False

    def getName(self):
        return self.name

    def getHp(self):
        return self.hp

    def getMaxHp(self):
        return self.maxHp

    def b_setHp(self, hp):
        self.setHp(hp)
        self.d_setHp(hp)

    def d_setHp(self, hp):
        self.sendUpdate('setHp', [int(hp)])

    def setHp(self, hp):
        self.hp = int(hp)

    def takeHackSlashDamage(self, amount, attackerId=None):
        if self._defeated:
            return 0
        damage = max(0, int(amount))
        newHp = max(0, self.hp - damage)
        self.b_setHp(newHp)
        if newHp <= 0:
            self.__defeat(attackerId)
        return damage

    def requestHackSlashHit(self, damage):
        """Client melee RPC: SoftTarget applyHackSlashHit → AI damage."""
        if self._defeated:
            return
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if toon is None:
            return
        # Same-zone gate keeps random cross-shard smackdowns out of reclaim demos.
        if getattr(toon, 'zoneId', None) != self.zoneId:
            return
        amount = max(0, min(80, int(damage)))
        if amount <= 0:
            return
        self.takeHackSlashDamage(amount, attackerId=avId)

    # Alias for magic-word / future melee hit events.
    takeDamage = takeHackSlashDamage

    def __defeat(self, attackerId=None):
        if self._defeated:
            return
        self._defeated = True
        self.sendUpdate('announceDefeat', [])
        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is not None:
            pollutionMgr.onCorruptToonDefeated(self.zoneId)
        # Brief delay so clients can play splat, then delete.
        taskMgr.doMethodLater(
            0.5, self.__deleteTask, self.uniqueName('corrupt-toon-delete'))

    def __deleteTask(self, task):
        if not self.isDeleted():
            self.requestDelete()
        return task.done

    def delete(self):
        taskMgr.remove(self.uniqueName('corrupt-toon-delete'))
        DistributedNodeAI.delete(self)

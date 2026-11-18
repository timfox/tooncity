import math

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.HackSlashTarget import HackSlashTarget
from toontown.toon.DistributedToonAI import DistributedToonAI


class DistributedCorruptToonAI(DistributedNodeAI, HackSlashTarget):
    """Hostile corrupt toon: chase / spit telegraph, defeat → pollution reclaim."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCorruptToonAI')

    def __init__(self, air, name=None, maxHp=None, archetype=None):
        DistributedNodeAI.__init__(self, air)
        self.archetype = CorruptionGlobals.normalizeArchetype(
            CorruptionGlobals.ARCHETYPE_SMUDGE if archetype is None else archetype)
        stats = CorruptionGlobals.archetypeStats(self.archetype)
        self.name = name or stats['defaultName']
        self.maxHp = (
            maxHp if maxHp is not None else int(stats['defaultHp']))
        self.hp = self.maxHp
        self._defeated = False
        self._attacking = False
        self._targetId = None
        self._attackReadyAt = 0.0

    def generate(self):
        DistributedNodeAI.generate(self)
        taskMgr.doMethodLater(
            CorruptionGlobals.AI_TICK_DT,
            self.__aiTick,
            self.uniqueName('corrupt-ai'))

    def getName(self):
        return self.name

    def getHp(self):
        return self.hp

    def getMaxHp(self):
        return self.maxHp

    def getArchetype(self):
        return self.archetype

    def setArchetype(self, archetype):
        self.archetype = CorruptionGlobals.normalizeArchetype(archetype)

    def _stats(self):
        return CorruptionGlobals.archetypeStats(self.archetype)

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

    def __aiTick(self, task):
        if self._defeated or self.isDeleted():
            return Task.done
        if self._attacking:
            return Task.again

        stats = self._stats()
        target = self.__findNearestToon(stats['aggroRange'])
        if target is None:
            self._targetId = None
            return Task.again

        self._targetId = target.doId
        dist = self.__planarDist(target)
        engage = float(stats['engageRange'])
        if dist <= engage:
            now = globalClock.getFrameTime()
            if now >= self._attackReadyAt:
                self.__beginAttack(target, stats)
            return Task.again

        if dist <= float(stats['aggroRange']):
            self.__chaseToward(target, stats)
        return Task.again

    def __findNearestToon(self, aggroRange):
        best = None
        bestDist = float(aggroRange)
        for obj in list(self.air.doId2do.values()):
            if not isinstance(obj, DistributedToonAI):
                continue
            if getattr(obj, 'zoneId', None) != self.zoneId:
                continue
            if getattr(obj, 'hp', 1) <= 0:
                continue
            dist = self.__planarDist(obj)
            if dist < bestDist:
                bestDist = dist
                best = obj
        return best

    def __planarDist(self, other):
        try:
            dx = other.getX() - self.getX()
            dy = other.getY() - self.getY()
        except Exception:
            return 9999.0
        return math.sqrt(dx * dx + dy * dy)

    def __chaseToward(self, target, stats):
        try:
            tx, ty = target.getX(), target.getY()
            x, y, z = self.getX(), self.getY(), self.getZ()
        except Exception:
            return
        dx = tx - x
        dy = ty - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.05:
            return
        # Ranged brutes stop around engage range instead of hugging the toon.
        if stats.get('ranged'):
            stopAt = float(stats['engageRange']) * 0.85
            if dist <= stopAt:
                heading = -math.degrees(math.atan2(dx, dy))
                self.setH(heading)
                self.sendUpdate('setXYZH', [x, y, z, heading])
                return
        step = float(stats['chaseSpeed']) * CorruptionGlobals.AI_TICK_DT
        if step >= dist:
            nx, ny = tx, ty
        else:
            nx = x + dx / dist * step
            ny = y + dy / dist * step
        heading = -math.degrees(math.atan2(dx, dy))
        self.setPos(nx, ny, z)
        self.setH(heading)
        # Same compound broadcast pattern elevators / crushables use for Node pos.
        self.sendUpdate('setXYZH', [nx, ny, z, heading])

    def __beginAttack(self, target, stats):
        self._attacking = True
        self._targetId = target.doId
        self.sendUpdate('announceAttackTelegraph', [])
        taskMgr.doMethodLater(
            float(stats['telegraphDelay']),
            self.__resolveAttack,
            self.uniqueName('corrupt-attack'))

    def __resolveAttack(self, task):
        self._attacking = False
        stats = self._stats()
        self._attackReadyAt = (
            globalClock.getFrameTime() + float(stats['attackCooldown']))
        if self._defeated or self.isDeleted():
            return Task.done
        target = self.air.doId2do.get(self._targetId)
        if target is None or not isinstance(target, DistributedToonAI):
            return Task.done
        if getattr(target, 'zoneId', None) != self.zoneId:
            return Task.done
        if getattr(target, 'hp', 1) <= 0:
            return Task.done
        if self.__planarDist(target) > float(stats['attackHitRange']):
            return Task.done
        # Honor client-reported dodge / hit i-frames (PollutionManager.requestHackSlashIFrame).
        iframeUntil = float(getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
        if globalClock.getFrameTime() < iframeUntil:  # noqa: F821
            self.notify.debug('attack whiffed — av %s i-framed' % self._targetId)
            return Task.done
        try:
            target.takeDamage(int(stats['attackDamage']))
        except Exception:
            self.notify.debug('takeDamage failed on av %s' % self._targetId)
        self.sendUpdate('announceAttackHit', [])
        return Task.done

    def __defeat(self, attackerId=None):
        if self._defeated:
            return
        self._defeated = True
        self._attacking = False
        taskMgr.remove(self.uniqueName('corrupt-ai'))
        taskMgr.remove(self.uniqueName('corrupt-attack'))
        self.sendUpdate('announceDefeat', [])
        pollutionMgr = getattr(self.air, 'pollutionManager', None)
        if pollutionMgr is not None:
            pollutionMgr.onCorruptToonDefeated(self.zoneId)
        # Brief delay so clients can play splat / purity pop, then delete.
        taskMgr.doMethodLater(
            CorruptionGlobals.DEFEAT_DELETE_DELAY,
            self.__deleteTask,
            self.uniqueName('corrupt-toon-delete'))

    def __deleteTask(self, task):
        if not self.isDeleted():
            self.requestDelete()
        return Task.done

    def delete(self):
        taskMgr.remove(self.uniqueName('corrupt-ai'))
        taskMgr.remove(self.uniqueName('corrupt-attack'))
        taskMgr.remove(self.uniqueName('corrupt-toon-delete'))
        DistributedNodeAI.delete(self)

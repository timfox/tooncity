import math

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.HackSlashTarget import HackSlashTarget
from toontown.toon.DistributedToonAI import DistributedToonAI


class DistributedCorruptToonAI(DistributedNodeAI, HackSlashTarget):
    """Hostile corrupt toon: chase, telegraphed smack, defeat → pollution reclaim.

    Ink Overlord (finalePhase 1/2) uses phase combat instead of Smudge chase:
    P1 ink-rain AoE, P2 enrage rain + close slam. Street archetypes unchanged.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCorruptToonAI')

    def __init__(self, air, name=None, maxHp=None, archetype=None,
                 finalePhase=0):
        DistributedNodeAI.__init__(self, air)
        self.archetype = (
            CorruptionGlobals.ARCHETYPE_INK
            if archetype is None else int(archetype))
        stats = CorruptionGlobals.archetypeStats(self.archetype)
        self.name = name or stats.get(
            'name', CorruptionGlobals.CORRUPT_TOON_DEFAULT_NAME)
        baseHp = (
            CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
            if maxHp is None else int(maxHp))
        self.maxHp = max(1, int(round(baseHp * float(stats.get('hpScale', 1.0)))))
        self.hp = self.maxHp
        self._defeated = False
        self._attacking = False
        self._targetId = None
        self._attackReadyAt = 0.0
        self._stats = stats
        self._attackMove = 'smack'
        self._puddleXY = None
        self.finalePhase = 0
        self.setFinalePhase(finalePhase)

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
        return int(self.archetype)

    def setArchetype(self, archetype):
        self.archetype = int(archetype)
        self._stats = CorruptionGlobals.archetypeStats(self.archetype)
        self._applyOverlordCombatStats()

    def getFinalePhase(self):
        return int(self.finalePhase)

    def setFinalePhase(self, phase):
        """Bind Overlord phase combat (0 = street archetype AI)."""
        self.finalePhase = CorruptionGlobals.normalizeFinalePhase(phase)
        self._applyOverlordCombatStats()

    def _applyOverlordCombatStats(self):
        """Overlay Overlord phase combat onto archetype base stats."""
        base = CorruptionGlobals.archetypeStats(self.archetype)
        combat = CorruptionGlobals.overlordPhaseCombat(self.finalePhase)
        if not combat:
            self._stats = dict(base)
            return
        merged = dict(base)
        for key in (
                'chaseSpeed', 'meleeRange', 'attackHitRange',
                'attackNearMissRange', 'attackDamage', 'telegraphDelay',
                'attackCooldown'):
            if key in combat:
                merged[key] = combat[key]
        merged['aoe'] = bool(combat.get('aoe', False))
        merged['moveMode'] = str(combat.get('moveMode', 'rain'))
        for key in (
                'slamHitRange', 'slamNearMissRange', 'slamDamage',
                'slamTelegraphDelay', 'slamCooldown', 'slamMeleeRange'):
            if key in combat:
                merged[key] = combat[key]
        self._stats = merged

    def _isOverlord(self):
        return int(self.finalePhase) >= 1

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
        # Balloon Snare string-snap punish: melee mid-telegraph cancels the
        # wind-up so the zip-flier feels fair to counter.
        if newHp > 0:
            self.__maybeInterruptSnareTelegraph()
        if newHp <= 0:
            self.__defeat(attackerId)
        return damage

    def __maybeInterruptSnareTelegraph(self):
        """Cancel Snare wind-up when punished mid-string telegraph."""
        if not self._attacking:
            return
        if not getattr(
                CorruptionGlobals, 'SNARE_STRING_COUNTER_INTERRUPT', True):
            return
        if (CorruptionGlobals.normalizeArchetype(self.archetype)
                != CorruptionGlobals.ARCHETYPE_SNARE):
            return
        self._attacking = False
        self._puddleXY = None
        try:
            taskMgr.remove(self.uniqueName('corrupt-attack'))
        except Exception:
            pass
        # Brief recovery so a successful punish doesn't chain into an instant
        # re-telegraph — still snappier than a full miss cooldown.
        cool = float(self._stats.get(
            'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN))
        self._attackReadyAt = (
            globalClock.getFrameTime() + max(0.2, cool * 0.45))  # noqa: F821
        self.notify.debug('snare string-snap interrupt — wind-up cancelled')

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

        target = self.__findNearestToon()
        if target is None:
            self._targetId = None
            return Task.again

        self._targetId = target.doId
        dist = self.__planarDist(target)
        engage = self.__engageRange()
        if dist <= engage:
            now = globalClock.getFrameTime()
            if now >= self._attackReadyAt:
                self.__beginAttack(target)
            return Task.again

        if dist <= CorruptionGlobals.AGGRO_RANGE:
            self.__chaseToward(target)
        return Task.again

    def __engageRange(self):
        """Distance at which the AI starts a telegraphed attack."""
        if self._isOverlord() and self._stats.get('moveMode') == 'enrage':
            # Enrage: slam when close, else rain from mid-range.
            slamEngage = float(self._stats.get(
                'slamMeleeRange', self._stats.get('meleeRange', 5.2)))
            rainEngage = float(self._stats.get(
                'meleeRange', CorruptionGlobals.MELEE_RANGE))
            return max(slamEngage, rainEngage)
        return float(self._stats.get('meleeRange', CorruptionGlobals.MELEE_RANGE))

    def __findNearestToon(self):
        best = None
        bestDist = CorruptionGlobals.AGGRO_RANGE
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

    def __iterZoneToons(self):
        for obj in list(self.air.doId2do.values()):
            if not isinstance(obj, DistributedToonAI):
                continue
            if getattr(obj, 'zoneId', None) != self.zoneId:
                continue
            if getattr(obj, 'hp', 1) <= 0:
                continue
            yield obj

    def __planarDist(self, other):
        try:
            dx = other.getX() - self.getX()
            dy = other.getY() - self.getY()
        except Exception:
            return 9999.0
        return math.sqrt(dx * dx + dy * dy)

    def __chaseToward(self, target):
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
        chase = float(self._stats.get('chaseSpeed', CorruptionGlobals.CHASE_SPEED))
        step = chase * CorruptionGlobals.AI_TICK_DT
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

    def __beginAttack(self, target):
        self._attacking = True
        self._targetId = target.doId
        if self._isOverlord():
            move = self.__pickOverlordMove(target)
            self._puddleXY = None
        else:
            move = str(self._stats.get('attackMove', 'smack') or 'smack')
            # Gunk Gagster: snapshot target XY at wind-up so the puddle lands
            # where they stood — dodge out during telegraph to escape the trap.
            if move == 'gag_lob':
                try:
                    self._puddleXY = (float(target.getX()), float(target.getY()))
                except Exception:
                    self._puddleXY = (float(self.getX()), float(self.getY()))
            else:
                self._puddleXY = None
        self._attackMove = move
        self.sendUpdate('announceAttackTelegraph', [])
        delay = self.__telegraphDelayForMove(move)
        taskMgr.doMethodLater(
            delay,
            self.__resolveAttack,
            self.uniqueName('corrupt-attack'))

    def __pickOverlordMove(self, target):
        """P1 always rains; P2 slams in close range else rains."""
        mode = str(self._stats.get('moveMode', 'rain'))
        if mode != 'enrage':
            return 'rain'
        dist = self.__planarDist(target)
        slamRange = float(self._stats.get(
            'slamMeleeRange', self._stats.get('slamHitRange', 5.2)))
        if dist <= slamRange:
            return 'slam'
        return 'rain'

    def __telegraphDelayForMove(self, move):
        if move == 'slam':
            return float(self._stats.get(
                'slamTelegraphDelay',
                self._stats.get(
                    'telegraphDelay', CorruptionGlobals.ATTACK_TELEGRAPH_DELAY)))
        return float(self._stats.get(
            'telegraphDelay', CorruptionGlobals.ATTACK_TELEGRAPH_DELAY))

    def __cooldownForMove(self, move):
        if move == 'slam':
            return float(self._stats.get(
                'slamCooldown',
                self._stats.get(
                    'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN)))
        return float(self._stats.get(
            'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN))

    def __hitRangesForMove(self, move):
        if move == 'slam':
            hit = float(self._stats.get(
                'slamHitRange', CorruptionGlobals.ATTACK_HIT_RANGE))
            near = float(self._stats.get(
                'slamNearMissRange', CorruptionGlobals.ATTACK_NEAR_MISS_RANGE))
            return hit, near
        hit = float(self._stats.get(
            'attackHitRange', CorruptionGlobals.ATTACK_HIT_RANGE))
        near = float(self._stats.get(
            'attackNearMissRange', CorruptionGlobals.ATTACK_NEAR_MISS_RANGE))
        return hit, near

    def __damageForMove(self, move):
        if move == 'slam':
            return int(self._stats.get(
                'slamDamage',
                self._stats.get('attackDamage', CorruptionGlobals.ATTACK_DAMAGE)))
        return int(self._stats.get(
            'attackDamage', CorruptionGlobals.ATTACK_DAMAGE))

    def __resolveAttack(self, task):
        self._attacking = False
        move = getattr(self, '_attackMove', 'smack') or 'smack'
        cool = self.__cooldownForMove(move)
        self._attackReadyAt = globalClock.getFrameTime() + cool  # noqa: F821
        if self._defeated or self.isDeleted():
            return Task.done

        if self._isOverlord() and move == 'rain' and self._stats.get('aoe'):
            return self.__resolveOverlordRain()
        if move == 'gag_lob':
            return self.__resolveGagsterPuddle()
        return self.__resolveSingleTargetHit(move)

    def __resolveGagsterPuddle(self):
        """Teal gag-lob puddle — AoE at the wind-up snapshot, not at self.

        Distinct from Smudge/Brute/Snare single-target smack and Overlord rain
        (self-centered). Players who dodge out of the lob zone during telegraph
        escape; anyone still standing in the puddle takes damage.
        """
        puddle = self._puddleXY
        self._puddleXY = None
        if puddle is None:
            # Fallback: treat as single-target if snapshot failed.
            return self.__resolveSingleTargetHit('gag_lob')
        px, py = puddle
        hitRange, nearMiss = self.__hitRangesForMove('gag_lob')
        dmg = self.__damageForMove('gag_lob')
        now = globalClock.getFrameTime()  # noqa: F821
        anyHit = False
        anyDodge = False
        for target in self.__iterZoneToons():
            try:
                dx = float(target.getX()) - px
                dy = float(target.getY()) - py
            except Exception:
                continue
            dist = math.sqrt(dx * dx + dy * dy)
            iframeUntil = float(
                getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
            iframes = now < iframeUntil
            if iframes and dist <= max(hitRange, nearMiss):
                anyDodge = True
                continue
            if dist > hitRange:
                continue
            try:
                target.takeDamage(dmg)
                anyHit = True
            except Exception:
                self.notify.debug(
                    'gag_lob takeDamage failed on av %s' % getattr(
                        target, 'doId', '?'))
        if anyHit:
            self.sendUpdate('announceAttackHit', [])
        elif anyDodge:
            self.sendUpdate('announceAttackDodged', [])
        return Task.done

    def __resolveOverlordRain(self):
        """Ink-rain AoE — damage every in-zone toon inside the puddle radius."""
        hitRange, nearMiss = self.__hitRangesForMove('rain')
        dmg = self.__damageForMove('rain')
        now = globalClock.getFrameTime()  # noqa: F821
        anyHit = False
        anyDodge = False
        for target in self.__iterZoneToons():
            dist = self.__planarDist(target)
            iframeUntil = float(
                getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
            iframes = now < iframeUntil
            if iframes and dist <= max(hitRange, nearMiss):
                anyDodge = True
                continue
            if dist > hitRange:
                continue
            try:
                target.takeDamage(dmg)
                anyHit = True
            except Exception:
                self.notify.debug(
                    'rain takeDamage failed on av %s' % getattr(
                        target, 'doId', '?'))
        if anyHit:
            self.sendUpdate('announceAttackHit', [])
        elif anyDodge:
            self.sendUpdate('announceAttackDodged', [])
        return Task.done

    def __resolveSingleTargetHit(self, move='smack'):
        target = self.air.doId2do.get(self._targetId)
        if target is None or not isinstance(target, DistributedToonAI):
            return Task.done
        if getattr(target, 'zoneId', None) != self.zoneId:
            return Task.done
        if getattr(target, 'hp', 1) <= 0:
            return Task.done
        hitRange, nearMiss = self.__hitRangesForMove(move)
        dist = self.__planarDist(target)
        # Honor client-reported dodge / hit i-frames (PollutionManager.requestHackSlashIFrame).
        iframeUntil = float(getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
        iframes = globalClock.getFrameTime() < iframeUntil  # noqa: F821
        if iframes and dist <= max(hitRange, nearMiss):
            # Hit eaten by i-frames, or near-miss while i-frames are live.
            self.notify.debug(
                'attack dodged — av %s i-framed (dist=%.2f move=%s)' % (
                    self._targetId, dist, move))
            self.sendUpdate('announceAttackDodged', [])
            return Task.done
        if dist > hitRange:
            return Task.done
        dmg = self.__damageForMove(move)
        try:
            target.takeDamage(dmg)
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

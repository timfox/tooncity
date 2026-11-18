import math

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.HackSlashTarget import HackSlashTarget
from toontown.hackslash import HackSlashConfig
from toontown.toon.DistributedToonAI import DistributedToonAI


class DistributedCorruptToonAI(DistributedNodeAI, HackSlashTarget):
    """Hostile corrupt toon: chase, telegraphed smack, defeat → pollution reclaim.

    Ink Overlord (finalePhase 1/2) uses phase combat instead of Smudge chase:
    P1 ink-rain AoE, P2 enrage rain + close slam. Street archetypes unchanged.

    Air-juggle hang stuns chase/attack on the AI so cancel→slam is not just
    client juice under multi-enemy pressure.
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
        # Absolute frame-time until which chase/attack stay paused (juggle hang).
        self._juggleHangStunUntil = 0.0
        self._puddleLinger = None
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

    def promoteFinalePhase(self, phase):
        """Mid-fight Overlord phase promote (street HP-threshold Unleash).

        Applies P2 combat stats and cancels an in-flight telegraph so the
        next wind-up uses rain/slam enrage. Client AV reads phase from the
        reclaim director — no DC finalePhase field required.
        """
        newPhase = CorruptionGlobals.normalizeFinalePhase(phase)
        if newPhase < 1 or newPhase <= int(self.finalePhase):
            return False
        self.setFinalePhase(newPhase)
        self.__interruptAttackForPhasePromote()
        return True

    def __interruptAttackForPhasePromote(self):
        """Drop current telegraph so Unleashed kit owns the next beat."""
        if not self._attacking:
            return
        self._attacking = False
        self._puddleXY = None
        try:
            taskMgr.remove(self.uniqueName('corrupt-attack'))
        except Exception:
            pass
        cool = float(self._stats.get(
            'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN))
        self._attackReadyAt = (
            globalClock.getFrameTime() + max(0.15, cool * 0.35))  # noqa: F821

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
        # Snare interrupt does not clear an already-landed Gagster linger
        # sludge — that hazard is independent of this unit's wind-up.
        # Brief recovery so a successful punish doesn't chain into an instant
        # re-telegraph — still snappier than a full miss cooldown.
        cool = float(self._stats.get(
            'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN))
        self._attackReadyAt = (
            globalClock.getFrameTime() + max(0.2, cool * 0.45))  # noqa: F821
        self.notify.debug('snare string-snap interrupt — wind-up cancelled')

    def requestHackSlashHit(self, damage, hitIndex=0):
        """Client melee RPC: SoftTarget applyHackSlashHit → AI damage + hang stun."""
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
        idx = max(0, min(255, int(hitIndex)))
        self.takeHackSlashDamage(amount, attackerId=avId)
        # Launch beats arm hang stun even if the hit finished the hostile —
        # __defeat already stops AI; stun is a no-op after delete.
        if not self._defeated:
            self.__applyJuggleHangStun(idx)

    def __applyJuggleHangStun(self, hitIndex):
        """Pause chase/attack for launch hang so cancel→slam sticks."""
        if not getattr(HackSlashConfig, 'JUGGLE_HANG_STUN_ENABLED', True):
            return
        if not HackSlashConfig.isJuggleHangStunHit(hitIndex):
            return
        sec = float(HackSlashConfig.juggleHangStunSec(hitIndex))
        if sec <= 0.0:
            return
        until = globalClock.getFrameTime() + sec  # noqa: F821
        if until > self._juggleHangStunUntil:
            self._juggleHangStunUntil = until
        # Cancel any in-flight telegraph so a resolving smack doesn't undermine
        # the hang (Snare already interrupts on melee; this covers all archetypes).
        self.__cancelAttackForJuggleHang()
        self.notify.debug(
            'juggle hang stun %.2fs (hitIndex=%s)' % (sec, hitIndex))

    def __cancelAttackForJuggleHang(self):
        """Drop wind-up / resolve task while juggle-hang stun is active."""
        if not self._attacking:
            return
        self._attacking = False
        self._puddleXY = None
        try:
            taskMgr.remove(self.uniqueName('corrupt-attack'))
        except Exception:
            pass
        # Short recovery so stun end doesn't instantly re-telegraph.
        cool = float(self._stats.get(
            'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN))
        self._attackReadyAt = max(
            self._attackReadyAt,
            globalClock.getFrameTime() + max(0.15, cool * 0.35))  # noqa: F821

    def isJuggleHangStunned(self, now=None):
        """True while air-juggle hang stun is holding chase/attack."""
        if now is None:
            now = globalClock.getFrameTime()  # noqa: F821
        return HackSlashConfig.isJuggleHangStunned(
            self._juggleHangStunUntil, now)

    # Alias for magic-word / future melee hit events.
    takeDamage = takeHackSlashDamage

    def __aiTick(self, task):
        if self._defeated or self.isDeleted():
            return Task.done
        if self._attacking:
            return Task.again
        # Air-juggle hang: stay put — no chase, no fresh telegraph.
        if self.isJuggleHangStunned():
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
        """Teal gag-lob puddle — AoE at the wind-up snapshot, then linger.

        Distinct from Smudge/Brute/Snare single-target smack and Overlord rain
        (self-centered). Players who dodge out of the lob zone during telegraph
        escape the land hit; the puddle then leaves a short sludge hazard that
        ticks DoT / stamps slow while anyone stays inside.
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
        # Arm linger sludge after land resolve — trap fantasy vs one-shot.
        self.__armGagsterPuddleLinger(px, py, hitRange)
        return Task.done

    def __armGagsterPuddleLinger(self, px, py, hitRange=None):
        """Leave a short-lived sludge hazard at the lob landing XY."""
        self.__clearGagsterPuddleLinger()
        if not getattr(
                CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_ENABLED', True):
            return
        lingerSec = float(self._stats.get(
            'puddleLingerSec',
            getattr(CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_SEC', 2.5)))
        tickSec = float(self._stats.get(
            'puddleLingerTickSec',
            getattr(CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_TICK_SEC', 0.5)))
        if lingerSec <= 0.0 or tickSec <= 0.0:
            return
        if hitRange is None:
            hitRange, _near = self.__hitRangesForMove('gag_lob')
        radius = float(hitRange or getattr(
            CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_RADIUS', 5.0))
        tickDmg = CorruptionGlobals.gagsterPuddleLingerTickDamage(self._stats)
        slowFactor = float(self._stats.get(
            'puddleLingerSlowFactor',
            getattr(
                CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_SLOW_FACTOR', 0.55)))
        now = globalClock.getFrameTime()  # noqa: F821
        self._puddleLinger = {
            'xy': (float(px), float(py)),
            'until': CorruptionGlobals.gagsterPuddleLingerUntil(now, lingerSec),
            'radius': radius,
            'tickDamage': tickDmg,
            'slowFactor': slowFactor,
            'tickSec': max(0.1, tickSec),
        }
        taskMgr.doMethodLater(
            self._puddleLinger['tickSec'],
            self.__tickGagsterPuddleLinger,
            self.uniqueName('gagster-puddle-linger'))

    def __tickGagsterPuddleLinger(self, task):
        """Periodic DoT + slow stamp while toons stand in linger sludge."""
        linger = getattr(self, '_puddleLinger', None)
        if linger is None or self.isDeleted():
            self._puddleLinger = None
            return Task.done
        now = globalClock.getFrameTime()  # noqa: F821
        if now >= float(linger['until']):
            self._puddleLinger = None
            return Task.done
        px, py = linger['xy']
        radius = float(linger['radius'])
        dmg = int(linger['tickDamage'])
        slowFactor = float(linger['slowFactor'])
        for target in self.__iterZoneToons():
            try:
                dx = float(target.getX()) - px
                dy = float(target.getY()) - py
            except Exception:
                continue
            if not CorruptionGlobals.isInsideGagsterPuddle(dx, dy, radius):
                continue
            iframeUntil = float(
                getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
            if now < iframeUntil:
                continue
            try:
                target.takeDamage(dmg)
            except Exception:
                self.notify.debug(
                    'gagster linger takeDamage failed on av %s' % getattr(
                        target, 'doId', '?'))
                continue
            # AI-side slow stamp (mirrors hackSlashIFrameUntil authority).
            # Client DistributedCorruptToon applies walk-slow while overlapping.
            target.hackSlashGagsterSludgeUntil = (
                CorruptionGlobals.gagsterPuddleSlowUntil(now))
            target.hackSlashGagsterSludgeSlow = slowFactor
        # No announceAttackHit — land already fired impact AV; ticks are quiet.
        return Task.again

    def __clearGagsterPuddleLinger(self):
        self._puddleLinger = None
        try:
            taskMgr.remove(self.uniqueName('gagster-puddle-linger'))
        except Exception:
            pass

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
        self._juggleHangStunUntil = 0.0
        taskMgr.remove(self.uniqueName('corrupt-ai'))
        taskMgr.remove(self.uniqueName('corrupt-attack'))
        # Keep linger sludge armed through the defeat delete delay so a
        # last-second lob still leaves a readable trap after the Gagster pops.
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
        self.__clearGagsterPuddleLinger()
        taskMgr.remove(self.uniqueName('corrupt-ai'))
        taskMgr.remove(self.uniqueName('corrupt-attack'))
        taskMgr.remove(self.uniqueName('corrupt-toon-delete'))
        DistributedNodeAI.delete(self)

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
    P1 ink-rain AoE + close slam, P2 enrage rain + mid ink_surge + close
    slam. Street archetypes use role AI (Gagster kite, Brute hold, Snare
    flank) so wave-script pack intent survives after combat starts — not all
    nearest-chase.

    Sludge Brute fires a traveling spit projectile (trail + land splash) from
    hold range, with a close slam secondary — not an instant long-range smack.

    Corrupted Oswald (finale betrayal chase) uses a distinct betrayal kit —
    ``betrayal_lunge`` dash-then-hit plus close ``stain_burst`` AoE and a
    planar shove — not a crimson Ink Smudge smack reskin.

    Ink Smudge (Act 1 spine + Overlord P2 adds) uses ``ink_dash`` rush plus
    close ``ink_splat`` AoE secondary — swarm pressure with move identity,
    not default smack fodder.

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
        self._spitAimXY = None
        self._spitProjectile = None
        # Absolute frame-time until which chase/attack stay paused (juggle hang).
        self._juggleHangStunUntil = 0.0
        self._puddleLinger = None
        self._rainLinger = None
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
                'slamTelegraphDelay', 'slamCooldown', 'slamMeleeRange',
                'surgeMaxRange', 'surgeDash', 'surgeStop', 'surgeHitRange',
                'surgeNearMissRange', 'surgeDamage', 'surgeTelegraphDelay',
                'surgeCooldown',
                'rainLingerSec', 'rainLingerTickSec', 'rainLingerTickDamage',
                'rainLingerSlowFactor'):
            if key in combat:
                merged[key] = combat[key]
        self._stats = merged

    def _isOverlord(self):
        return int(self.finalePhase) >= 1

    def promoteFinalePhase(self, phase):
        """Mid-fight Overlord phase promote (street HP-threshold Unleash).

        Applies P2 combat stats and cancels an in-flight telegraph so the
        next wind-up uses rain/surge/slam enrage. Client AV reads phase from
        the reclaim director — no DC finalePhase field required.
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
        self._spitAimXY = None
        self.__clearBruteSpitProjectile()
        # Keep any already-landed rain linger — phase flip does not erase
        # arena sludge (parity with Gagster land linger across interrupts).
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
        # Melee mid-telegraph punish: cancel Snare string / Brute spit /
        # Gagster lob / Overlord rain·slam·ink_surge / Smudge ink_dash·
        # ink_splat / Oswald betrayal_lunge·stain_burst wind-ups so street
        # kits, swarm adds, climax, and twist chase telegraphs feel fair
        # to interrupt.
        if newHp > 0:
            self.__maybeInterruptMeleeTelegraph()
        if newHp <= 0:
            self.__defeat(attackerId)
        return damage

    def __maybeInterruptMeleeTelegraph(self):
        """Cancel interruptible wind-ups mid-telegraph (street + Smudge + Overlord + Oswald)."""
        if not self._attacking:
            return
        move = getattr(self, '_attackMove', 'smack') or 'smack'
        if not CorruptionGlobals.isMeleeInterruptibleTelegraph(
                self.archetype, move):
            return
        self._attacking = False
        # Clear wind-up aim snapshots only — do not drop an already-landed
        # Gagster linger sludge (independent of this unit's telegraph).
        self._puddleXY = None
        self._spitAimXY = None
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
        self.notify.debug(
            'melee telegraph interrupt (%s) — wind-up cancelled' % move)

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
        self._spitAimXY = None
        self.__clearBruteSpitProjectile()
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
            # Role AI: Gagster kite / Brute hold / Snare flank (Smudge chase).
            self.__roleMoveToward(target)
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
        # Sludge Brute: spit from hold-plant range (meleeRange); slam is closer.
        if (CorruptionGlobals.normalizeArchetype(self.archetype)
                == CorruptionGlobals.ARCHETYPE_BRUTE):
            spitEngage = float(self._stats.get(
                'meleeRange', CorruptionGlobals.MELEE_RANGE))
            slamEngage = float(self._stats.get(
                'slamMeleeRange', spitEngage))
            return max(spitEngage, slamEngage)
        # Corrupted Oswald: lunge from mid-range; stain burst is closer.
        if (CorruptionGlobals.normalizeArchetype(self.archetype)
                == CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD):
            lungeEngage = float(self._stats.get(
                'meleeRange', CorruptionGlobals.MELEE_RANGE))
            burstEngage = float(self._stats.get(
                'burstMeleeRange', lungeEngage))
            return max(lungeEngage, burstEngage)
        # Ink Smudge: ink-dash from mid-range; splat is closer.
        if (CorruptionGlobals.normalizeArchetype(self.archetype)
                == CorruptionGlobals.ARCHETYPE_INK):
            dashEngage = float(self._stats.get(
                'meleeRange', CorruptionGlobals.MELEE_RANGE))
            splatEngage = float(self._stats.get(
                'splatMeleeRange', dashEngage))
            return max(dashEngage, splatEngage)
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

    def __roleMoveToward(self, target):
        """Move with archetype role AI so pack scripts keep combat identity.

        Overlord / disabled / Smudge / Oswald → nearest chase. Gagster kites
        the lob ring, Brute plants in spit range, Snare approaches on a flank.
        """
        if self._isOverlord() or not getattr(
                CorruptionGlobals, 'ROLE_AI_ENABLED', True):
            self.__chaseToward(target)
            return
        role = CorruptionGlobals.archetypeCombatRole(self.archetype)
        if role == CorruptionGlobals.ROLE_CHASE:
            self.__chaseToward(target)
            return
        try:
            sx = float(self.getX())
            sy = float(self.getY())
            tx = float(target.getX())
            ty = float(target.getY())
        except Exception:
            return
        side = CorruptionGlobals.snareFlankSide(getattr(self, 'doId', 0))
        gx, gy, action = CorruptionGlobals.roleMoveGoal(
            role, sx, sy, tx, ty, flankSide=side)
        if action == 'hold':
            # Face the toon while planted so spit / lob telegraphs read.
            self.__faceTowardXY(tx, ty)
            return
        speedScale = CorruptionGlobals.roleMoveSpeedScale(role, action)
        self.__moveTowardXY(gx, gy, speedScale=speedScale)

    def __chaseToward(self, target):
        """Legacy nearest-chase — straight at the toon (Smudge / Overlord)."""
        try:
            tx, ty = target.getX(), target.getY()
        except Exception:
            return
        self.__moveTowardXY(tx, ty, speedScale=1.0)

    def __faceTowardXY(self, tx, ty):
        """Rotate toward a planar point without translating (hold plant)."""
        try:
            x, y, z = self.getX(), self.getY(), self.getZ()
        except Exception:
            return
        dx = float(tx) - x
        dy = float(ty) - y
        if (dx * dx + dy * dy) < 1e-6:
            return
        heading = -math.degrees(math.atan2(dx, dy))
        self.setH(heading)
        self.sendUpdate('setXYZH', [x, y, z, heading])

    def __moveTowardXY(self, tx, ty, speedScale=1.0):
        """Step toward planar (tx, ty) using chaseSpeed * speedScale."""
        try:
            x, y, z = self.getX(), self.getY(), self.getZ()
        except Exception:
            return
        dx = float(tx) - x
        dy = float(ty) - y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.05:
            return
        chase = float(self._stats.get('chaseSpeed', CorruptionGlobals.CHASE_SPEED))
        scale = max(0.05, float(speedScale or 1.0))
        step = chase * scale * CorruptionGlobals.AI_TICK_DT
        if step >= dist:
            nx, ny = float(tx), float(ty)
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
        self.__clearBruteSpitProjectile()
        if self._isOverlord():
            move = self.__pickOverlordMove(target)
            self._puddleXY = None
            self._spitAimXY = None
        else:
            move = str(self._stats.get('attackMove', 'smack') or 'smack')
            aid = CorruptionGlobals.normalizeArchetype(self.archetype)
            # Sludge Brute: spit by default; slam when the toon is in their face.
            if aid == CorruptionGlobals.ARCHETYPE_BRUTE and move == 'spit':
                move = CorruptionGlobals.brutePickAttackMove(
                    self.__planarDist(target), self._stats)
            # Ink Smudge: ink-dash by default; splat when the toon is in their face.
            elif (aid == CorruptionGlobals.ARCHETYPE_INK
                    and move in ('ink_dash', 'smack')):
                move = CorruptionGlobals.inkPickAttackMove(
                    self.__planarDist(target), self._stats)
            # Corrupted Oswald: betrayal lunge by default; stain burst up close.
            elif (aid == CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD
                    and move in ('betrayal_lunge', 'smack')):
                move = CorruptionGlobals.oswaldPickAttackMove(
                    self.__planarDist(target), self._stats)
            # Gunk Gagster: snapshot target XY at wind-up so the puddle lands
            # where they stood — dodge out during telegraph to escape the trap.
            if move == 'gag_lob':
                try:
                    self._puddleXY = (float(target.getX()), float(target.getY()))
                except Exception:
                    self._puddleXY = (float(self.getX()), float(self.getY()))
                self._spitAimXY = None
            elif move == 'spit':
                # Snapshot aim so the spit flies where they stood at wind-up.
                try:
                    self._spitAimXY = (
                        float(target.getX()), float(target.getY()))
                except Exception:
                    self._spitAimXY = (
                        float(self.getX()), float(self.getY()))
                self._puddleXY = None
            else:
                self._puddleXY = None
                self._spitAimXY = None
        self._attackMove = move
        # Pass move id so client Overlord AV can read rain vs slam vs ink_surge
        # (and street kits keep their own attackMove string).
        self.sendUpdate('announceAttackTelegraph', [str(move or '')])
        delay = self.__telegraphDelayForMove(move)
        taskMgr.doMethodLater(
            delay,
            self.__resolveAttack,
            self.uniqueName('corrupt-attack'))

    def __pickOverlordMove(self, target):
        """P1 picks slam / rain; P2 picks slam / ink_surge / rain by range."""
        mode = str(self._stats.get('moveMode', 'rain'))
        dist = self.__planarDist(target)
        if mode == 'enrage':
            return CorruptionGlobals.overlordPickEnrageMove(dist, self._stats)
        if mode == 'rising':
            return CorruptionGlobals.overlordPickRisingMove(dist, self._stats)
        return 'rain'

    def __telegraphDelayForMove(self, move):
        if move == 'slam':
            return float(self._stats.get(
                'slamTelegraphDelay',
                self._stats.get(
                    'telegraphDelay', CorruptionGlobals.ATTACK_TELEGRAPH_DELAY)))
        if move == 'ink_surge':
            return float(self._stats.get(
                'surgeTelegraphDelay',
                self._stats.get(
                    'telegraphDelay', CorruptionGlobals.ATTACK_TELEGRAPH_DELAY)))
        if move == 'stain_burst':
            return float(self._stats.get(
                'burstTelegraphDelay',
                self._stats.get(
                    'telegraphDelay', CorruptionGlobals.ATTACK_TELEGRAPH_DELAY)))
        if move == 'ink_splat':
            return float(self._stats.get(
                'splatTelegraphDelay',
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
        if move == 'ink_surge':
            return float(self._stats.get(
                'surgeCooldown',
                self._stats.get(
                    'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN)))
        if move == 'stain_burst':
            return float(self._stats.get(
                'burstCooldown',
                self._stats.get(
                    'attackCooldown', CorruptionGlobals.ATTACK_COOLDOWN)))
        if move == 'ink_splat':
            return float(self._stats.get(
                'splatCooldown',
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
        if move == 'ink_surge':
            hit = float(self._stats.get(
                'surgeHitRange',
                self._stats.get(
                    'attackHitRange', CorruptionGlobals.ATTACK_HIT_RANGE)))
            near = float(self._stats.get(
                'surgeNearMissRange',
                self._stats.get(
                    'attackNearMissRange',
                    CorruptionGlobals.ATTACK_NEAR_MISS_RANGE)))
            return hit, near
        if move == 'stain_burst':
            hit = float(self._stats.get(
                'burstHitRange', CorruptionGlobals.ATTACK_HIT_RANGE))
            near = float(self._stats.get(
                'burstNearMissRange',
                CorruptionGlobals.ATTACK_NEAR_MISS_RANGE))
            return hit, near
        if move == 'ink_splat':
            hit = float(self._stats.get(
                'splatHitRange', CorruptionGlobals.ATTACK_HIT_RANGE))
            near = float(self._stats.get(
                'splatNearMissRange',
                CorruptionGlobals.ATTACK_NEAR_MISS_RANGE))
            return hit, near
        if move == 'betrayal_lunge':
            hit = float(self._stats.get(
                'lungeHitRange',
                self._stats.get(
                    'attackHitRange', CorruptionGlobals.ATTACK_HIT_RANGE)))
            near = float(self._stats.get(
                'lungeNearMissRange',
                self._stats.get(
                    'attackNearMissRange',
                    CorruptionGlobals.ATTACK_NEAR_MISS_RANGE)))
            return hit, near
        if move == 'ink_dash':
            hit = float(self._stats.get(
                'dashHitRange',
                self._stats.get(
                    'attackHitRange', CorruptionGlobals.ATTACK_HIT_RANGE)))
            near = float(self._stats.get(
                'dashNearMissRange',
                self._stats.get(
                    'attackNearMissRange',
                    CorruptionGlobals.ATTACK_NEAR_MISS_RANGE)))
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
        if move == 'ink_surge':
            return int(self._stats.get(
                'surgeDamage',
                self._stats.get('attackDamage', CorruptionGlobals.ATTACK_DAMAGE)))
        if move == 'stain_burst':
            return int(self._stats.get(
                'burstDamage',
                self._stats.get('attackDamage', CorruptionGlobals.ATTACK_DAMAGE)))
        if move == 'ink_splat':
            return int(self._stats.get(
                'splatDamage',
                self._stats.get('attackDamage', CorruptionGlobals.ATTACK_DAMAGE)))
        if move == 'betrayal_lunge':
            return int(self._stats.get(
                'lungeDamage',
                self._stats.get('attackDamage', CorruptionGlobals.ATTACK_DAMAGE)))
        if move == 'ink_dash':
            return int(self._stats.get(
                'dashDamage',
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
        if self._isOverlord() and move == 'ink_surge':
            return self.__resolveOverlordInkSurge()
        if move == 'gag_lob':
            return self.__resolveGagsterPuddle()
        if move == 'spit':
            return self.__resolveBruteSpit()
        if move == 'stain_burst':
            return self.__resolveOswaldStainBurst()
        if move == 'betrayal_lunge':
            return self.__resolveOswaldBetrayalLunge()
        if move == 'ink_splat':
            return self.__resolveInkSplat()
        if move == 'ink_dash':
            return self.__resolveInkDash()
        return self.__resolveSingleTargetHit(move)

    def __resolveBruteSpit(self):
        """Launch a traveling spit projectile — not an instant long-range smack.

        Aim XY was snapshotted at wind-up (dodge sideways / out of the land
        splash during flight). Trail ticks chip along the path; land resolves
        splash damage and announceAttackHit. Falls back to single-target when
        projectile is disabled or aim snapshot failed.
        """
        if not getattr(
                CorruptionGlobals, 'BRUTE_SPIT_PROJECTILE_ENABLED', True):
            return self.__resolveSingleTargetHit('spit')
        aim = self._spitAimXY
        self._spitAimXY = None
        if aim is None:
            return self.__resolveSingleTargetHit('spit')
        try:
            ox = float(self.getX())
            oy = float(self.getY())
        except Exception:
            return Task.done
        maxRange = CorruptionGlobals.bruteSpitMaxRange(self._stats)
        lx, ly = CorruptionGlobals.bruteSpitAimPos(
            ox, oy, aim[0], aim[1], maxRange=maxRange)
        travel = CorruptionGlobals.bruteSpitTravelSec(self._stats)
        trailTick = CorruptionGlobals.bruteSpitTrailTickSec(self._stats)
        landRadius = CorruptionGlobals.bruteSpitLandRadius(self._stats)
        _, nearMiss = self.__hitRangesForMove('spit')
        self._spitProjectile = {
            'ox': ox,
            'oy': oy,
            'lx': lx,
            'ly': ly,
            't0': globalClock.getFrameTime(),  # noqa: F821
            'travel': travel,
            'trailRadius': CorruptionGlobals.bruteSpitTrailRadius(self._stats),
            'trailDamage': CorruptionGlobals.bruteSpitTrailDamage(self._stats),
            'landRadius': landRadius,
            'nearMiss': float(nearMiss),
            'landDamage': self.__damageForMove('spit'),
            'trailHitIds': set(),
            'anyHit': False,
            'anyDodge': False,
        }
        taskMgr.doMethodLater(
            trailTick,
            self.__tickBruteSpitProjectile,
            self.uniqueName('brute-spit-projectile'))
        return Task.done

    def __tickBruteSpitProjectile(self, task):
        """Advance spit along origin→land; trail chip, then land splash."""
        spit = getattr(self, '_spitProjectile', None)
        if spit is None or self.isDeleted() or self._defeated:
            self._spitProjectile = None
            return Task.done
        now = globalClock.getFrameTime()  # noqa: F821
        travel = max(0.05, float(spit['travel']))
        elapsed = now - float(spit['t0'])
        frac = elapsed / travel
        ox, oy = spit['ox'], spit['oy']
        lx, ly = spit['lx'], spit['ly']
        if frac < 1.0:
            px, py = CorruptionGlobals.bruteSpitPosAtFrac(
                ox, oy, lx, ly, frac)
            self.__applyBruteSpitSplash(
                spit, px, py,
                radius=float(spit['trailRadius']),
                damage=int(spit['trailDamage']),
                nearMiss=float(spit['nearMiss']),
                trailOnly=True)
            return Task.again
        # Land — full spit splash at clamped aim.
        self.__applyBruteSpitSplash(
            spit, lx, ly,
            radius=float(spit['landRadius']),
            damage=int(spit['landDamage']),
            nearMiss=float(spit['nearMiss']),
            trailOnly=False)
        if spit['anyHit']:
            self.sendUpdate('announceAttackHit', [])
        elif spit['anyDodge']:
            self.sendUpdate('announceAttackDodged', [])
        self._spitProjectile = None
        return Task.done

    def __damageToonAndCheckReclaimKo(self, target, dmg, context='hit'):
        """Apply takeDamage; if the toon goes sad, fail active street reclaim.

        Thin KO hook for explore→fight→reclaim: reclaim director marks the
        street contested (same as bail) so player knockout is an authored
        fail, not a silent pack continue. Looks up air.reclaimDirectors to
        avoid importing DistributedReclaimDirectorAI (circular with spawn).
        """
        try:
            target.takeDamage(int(dmg))
        except Exception:
            self.notify.debug(
                '%s takeDamage failed on av %s' % (
                    context, getattr(target, 'doId', '?')))
            return False
        if getattr(target, 'hp', 1) > 0:
            return True
        directors = getattr(self.air, 'reclaimDirectors', None) or {}
        zoneId = int(
            getattr(target, 'zoneId', 0)
            or getattr(self, 'zoneId', 0)
            or 0)
        director = directors.get(zoneId)
        if director is None:
            return True
        if getattr(director, 'isDeleted', lambda: True)():
            return True
        fail = getattr(director, 'failStreetOnKnockout', None)
        if callable(fail):
            try:
                fail(getattr(target, 'doId', None))
            except Exception:
                self.notify.debug(
                    'reclaim KO fail hook errored for av %s' % getattr(
                        target, 'doId', '?'))
        return True

    def __applyBruteSpitSplash(self, spit, px, py, radius, damage,
                               nearMiss, trailOnly):
        """Damage / dodge-stamp toons inside a spit trail or land splash."""
        now = globalClock.getFrameTime()  # noqa: F821
        trailIds = spit['trailHitIds']
        for target in self.__iterZoneToons():
            try:
                dx = float(target.getX()) - float(px)
                dy = float(target.getY()) - float(py)
                doId = int(getattr(target, 'doId', 0) or 0)
            except Exception:
                continue
            dist = math.sqrt(dx * dx + dy * dy)
            iframeUntil = float(
                getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
            iframes = now < iframeUntil
            inSplash = CorruptionGlobals.isInsideBruteSpitSplash(
                dx, dy, radius)
            if iframes and (inSplash or dist <= max(radius, nearMiss)):
                spit['anyDodge'] = True
                continue
            if not inSplash:
                continue
            if trailOnly:
                if doId and doId in trailIds:
                    continue
                if doId:
                    trailIds.add(doId)
            if self.__damageToonAndCheckReclaimKo(
                    target, int(damage), context='brute spit'):
                spit['anyHit'] = True

    def __clearBruteSpitProjectile(self):
        self._spitProjectile = None
        self._spitAimXY = None
        try:
            taskMgr.remove(self.uniqueName('brute-spit-projectile'))
        except Exception:
            pass

    def __resolveGagsterPuddle(self):
        """Teal gag-lob puddle — AoE at the wind-up snapshot, then linger.

        Distinct from Smudge/Snare single-target smack, Brute traveling spit,
        and Overlord rain (self-centered). Players who dodge out of the lob
        zone during telegraph escape the land hit; the puddle then leaves a
        short sludge hazard that ticks DoT / stamps slow while anyone stays
        inside.
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
            if self.__damageToonAndCheckReclaimKo(
                    target, dmg, context='gag_lob'):
                anyHit = True
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
            if not self.__damageToonAndCheckReclaimKo(
                    target, dmg, context='gagster linger'):
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
        """Ink-rain AoE — damage every in-zone toon inside the puddle radius.

        After the land tick, arm a short lingering sludge hazard at the
        boss XY (Gagster-like DoT / slow) so climax rain owns arena space.
        """
        try:
            ox = float(self.getX())
            oy = float(self.getY())
        except Exception:
            ox = oy = None
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
            if self.__damageToonAndCheckReclaimKo(
                    target, dmg, context='rain'):
                anyHit = True
        if anyHit:
            self.sendUpdate('announceAttackHit', [])
        elif anyDodge:
            self.sendUpdate('announceAttackDodged', [])
        # Arm linger sludge after rain resolve — arena trap vs one-shot.
        if ox is not None and oy is not None:
            self.__armOverlordRainLinger(ox, oy, hitRange)
        return Task.done

    def __armOverlordRainLinger(self, ox, oy, hitRange=None):
        """Leave a short-lived sludge hazard at the rain puddle XY."""
        self.__clearOverlordRainLinger()
        if not getattr(
                CorruptionGlobals, 'OVERLORD_RAIN_LINGER_ENABLED', True):
            return
        lingerSec = float(self._stats.get(
            'rainLingerSec',
            getattr(CorruptionGlobals, 'OVERLORD_RAIN_LINGER_SEC', 3.0)))
        tickSec = float(self._stats.get(
            'rainLingerTickSec',
            getattr(
                CorruptionGlobals, 'OVERLORD_RAIN_LINGER_TICK_SEC', 0.5)))
        if lingerSec <= 0.0 or tickSec <= 0.0:
            return
        if hitRange is None:
            hitRange, _near = self.__hitRangesForMove('rain')
        radius = float(hitRange or getattr(
            CorruptionGlobals, 'OVERLORD_RAIN_LINGER_RADIUS', 9.5))
        tickDmg = CorruptionGlobals.overlordRainLingerTickDamage(self._stats)
        slowFactor = float(self._stats.get(
            'rainLingerSlowFactor',
            getattr(
                CorruptionGlobals, 'OVERLORD_RAIN_LINGER_SLOW_FACTOR', 0.5)))
        now = globalClock.getFrameTime()  # noqa: F821
        self._rainLinger = {
            'xy': (float(ox), float(oy)),
            'until': CorruptionGlobals.overlordRainLingerUntil(
                now, lingerSec),
            'radius': radius,
            'tickDamage': tickDmg,
            'slowFactor': slowFactor,
            'tickSec': max(0.1, tickSec),
        }
        taskMgr.doMethodLater(
            self._rainLinger['tickSec'],
            self.__tickOverlordRainLinger,
            self.uniqueName('overlord-rain-linger'))

    def __tickOverlordRainLinger(self, task):
        """Periodic DoT + slow stamp while toons stand in rain linger sludge."""
        linger = getattr(self, '_rainLinger', None)
        if linger is None or self.isDeleted():
            self._rainLinger = None
            return Task.done
        now = globalClock.getFrameTime()  # noqa: F821
        if now >= float(linger['until']):
            self._rainLinger = None
            return Task.done
        ox, oy = linger['xy']
        radius = float(linger['radius'])
        dmg = int(linger['tickDamage'])
        slowFactor = float(linger['slowFactor'])
        for target in self.__iterZoneToons():
            try:
                dx = float(target.getX()) - ox
                dy = float(target.getY()) - oy
            except Exception:
                continue
            if not CorruptionGlobals.isInsideOverlordRainLinger(
                    dx, dy, radius):
                continue
            iframeUntil = float(
                getattr(target, 'hackSlashIFrameUntil', 0.0) or 0.0)
            if now < iframeUntil:
                continue
            if not self.__damageToonAndCheckReclaimKo(
                    target, dmg, context='overlord rain linger'):
                continue
            # AI-side slow stamp (mirrors Gagster linger authority).
            # Client DistributedCorruptToon applies walk-slow while overlapping.
            target.hackSlashOverlordRainSludgeUntil = (
                CorruptionGlobals.overlordRainSlowUntil(now))
            target.hackSlashOverlordRainSludgeSlow = slowFactor
        # No announceAttackHit — land already fired impact AV; ticks are quiet.
        return Task.again

    def __clearOverlordRainLinger(self):
        self._rainLinger = None
        try:
            taskMgr.remove(self.uniqueName('overlord-rain-linger'))
        except Exception:
            pass

    def __resolveOverlordInkSurge(self):
        """P2 mid-range ink surge — planar rush, then landing AoE.

        Third Unleashed note between close slam and far rain (gap scan #8).
        Boss closes a mid gap on resolve, then hits every toon inside the
        surge radius at the new position — distinct from stationary rain
        and face-hug slam. Falls back to rain when surge is disabled.
        Damage routes through ``__damageToonAndCheckReclaimKo`` only.
        """
        if not getattr(CorruptionGlobals, 'OVERLORD_INK_SURGE_ENABLED', True):
            return self.__resolveOverlordRain()
        target = self.air.doId2do.get(self._targetId)
        if target is not None and isinstance(target, DistributedToonAI):
            if (getattr(target, 'zoneId', None) == self.zoneId
                    and getattr(target, 'hp', 1) > 0):
                self.__surgeOverlordTowardTarget(target)
        try:
            ox = float(self.getX())
            oy = float(self.getY())
        except Exception:
            return Task.done
        hitRange, nearMiss = self.__hitRangesForMove('ink_surge')
        dmg = self.__damageForMove('ink_surge')
        now = globalClock.getFrameTime()  # noqa: F821
        anyHit = False
        anyDodge = False
        for toon in self.__iterZoneToons():
            try:
                dx = float(toon.getX()) - ox
                dy = float(toon.getY()) - oy
            except Exception:
                continue
            dist = math.sqrt(dx * dx + dy * dy)
            iframeUntil = float(
                getattr(toon, 'hackSlashIFrameUntil', 0.0) or 0.0)
            iframes = now < iframeUntil
            if iframes and dist <= max(hitRange, nearMiss):
                anyDodge = True
                continue
            if dist > hitRange:
                continue
            if self.__damageToonAndCheckReclaimKo(
                    toon, dmg, context='ink_surge'):
                anyHit = True
        if anyHit:
            self.sendUpdate('announceAttackHit', [])
        elif anyDodge:
            self.sendUpdate('announceAttackDodged', [])
        return Task.done

    def __surgeOverlordTowardTarget(self, target):
        """Planar surge step for ink_surge — longer boss rush than Smudge dash."""
        if target is None:
            return
        try:
            sx = float(self.getX())
            sy = float(self.getY())
            sz = float(self.getZ())
            tx = float(target.getX())
            ty = float(target.getY())
        except Exception:
            return
        dash = CorruptionGlobals.overlordSurgeDashDist(self._stats)
        stop = CorruptionGlobals.overlordSurgeStop(self._stats)
        nx, ny = CorruptionGlobals.overlordSurgePos(
            sx, sy, tx, ty, dash=dash, stop=stop)
        if abs(nx - sx) < 1e-6 and abs(ny - sy) < 1e-6:
            return
        heading = -math.degrees(math.atan2(tx - sx, ty - sy))
        self.setPos(nx, ny, sz)
        self.setH(heading)
        self.sendUpdate('setXYZH', [nx, ny, sz, heading])

    def __resolveOswaldBetrayalLunge(self):
        """False-friend rush: dash toward the toon, then single-target hit + shove.

        Distinct from stationary Smudge smack — Oswald closes the gap on
        resolve so the twist chase fights like a betrayal, not fodder.
        Falls back to single-target when the kit / lunge is disabled.
        """
        if not getattr(CorruptionGlobals, 'OSWALD_BETRAYAL_KIT_ENABLED', True):
            return self.__resolveSingleTargetHit('smack')
        if not getattr(CorruptionGlobals, 'OSWALD_BETRAYAL_LUNGE_ENABLED', True):
            return self.__resolveSingleTargetHit('betrayal_lunge')
        target = self.air.doId2do.get(self._targetId)
        if target is None or not isinstance(target, DistributedToonAI):
            return Task.done
        if getattr(target, 'zoneId', None) != self.zoneId:
            return Task.done
        if getattr(target, 'hp', 1) <= 0:
            return Task.done
        self.__dashOswaldTowardTarget(target)
        return self.__resolveSingleTargetHit('betrayal_lunge')

    def __resolveOswaldStainBurst(self):
        """Close crimson stain burst — self-centered AoE when Oswald is pressed.

        Distinct from Overlord rain (wider mid-range) and Gagster lob (wind-up
        snapshot). Dodge out of the burst radius during telegraph to escape.
        """
        if not getattr(CorruptionGlobals, 'OSWALD_BETRAYAL_KIT_ENABLED', True):
            return self.__resolveSingleTargetHit('smack')
        if not getattr(
                CorruptionGlobals, 'OSWALD_STAIN_BURST_SECONDARY_ENABLED', True):
            return self.__resolveOswaldBetrayalLunge()
        try:
            ox = float(self.getX())
            oy = float(self.getY())
        except Exception:
            return Task.done
        hitRange, nearMiss = self.__hitRangesForMove('stain_burst')
        dmg = self.__damageForMove('stain_burst')
        now = globalClock.getFrameTime()  # noqa: F821
        anyHit = False
        anyDodge = False
        for target in self.__iterZoneToons():
            try:
                dx = float(target.getX()) - ox
                dy = float(target.getY()) - oy
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
            if self.__damageToonAndCheckReclaimKo(
                    target, dmg, context='stain_burst'):
                anyHit = True
                self.__shoveTargetFromOswald(target)
        if anyHit:
            self.sendUpdate('announceAttackHit', [])
        elif anyDodge:
            self.sendUpdate('announceAttackDodged', [])
        return Task.done

    def __dashOswaldTowardTarget(self, target):
        """Planar dash step for betrayal_lunge — closes the false-friend gap."""
        if target is None:
            return
        try:
            sx = float(self.getX())
            sy = float(self.getY())
            sz = float(self.getZ())
            tx = float(target.getX())
            ty = float(target.getY())
        except Exception:
            return
        dash = CorruptionGlobals.oswaldLungeDashDist(self._stats)
        nx, ny = CorruptionGlobals.oswaldLungeDashPos(sx, sy, tx, ty, dash=dash)
        if abs(nx - sx) < 1e-6 and abs(ny - sy) < 1e-6:
            return
        heading = -math.degrees(math.atan2(tx - sx, ty - sy))
        self.setPos(nx, ny, sz)
        self.setH(heading)
        self.sendUpdate('setXYZH', [nx, ny, sz, heading])

    def __resolveInkDash(self):
        """Swarm rush: planar ink-dash toward the toon, then single-target hit.

        Act 1 / P2-add move identity — Smudge closes a short gap on resolve
        instead of standing smack. Shorter than Oswald betrayal_lunge; no
        shove. Falls back to single-target when the kit / dash is disabled.
        Damage routes through ``__damageToonAndCheckReclaimKo``.
        """
        if not getattr(CorruptionGlobals, 'INK_SMUDGE_KIT_ENABLED', True):
            return self.__resolveSingleTargetHit('smack')
        if not getattr(CorruptionGlobals, 'INK_DASH_ENABLED', True):
            return self.__resolveSingleTargetHit('ink_dash')
        target = self.air.doId2do.get(self._targetId)
        if target is None or not isinstance(target, DistributedToonAI):
            return Task.done
        if getattr(target, 'zoneId', None) != self.zoneId:
            return Task.done
        if getattr(target, 'hp', 1) <= 0:
            return Task.done
        self.__dashInkTowardTarget(target)
        return self.__resolveSingleTargetHit('ink_dash')

    def __resolveInkSplat(self):
        """Close purple ink splat — self-centered AoE when Smudge is pressed.

        Distinct from Oswald stain_burst (shove + crimson), Overlord rain
        (wider mid-range), and Gagster lob (wind-up snapshot). Dodge out of
        the splat radius during telegraph to escape. Damage routes through
        ``__damageToonAndCheckReclaimKo`` only.
        """
        if not getattr(CorruptionGlobals, 'INK_SMUDGE_KIT_ENABLED', True):
            return self.__resolveSingleTargetHit('smack')
        if not getattr(
                CorruptionGlobals, 'INK_SPLAT_SECONDARY_ENABLED', True):
            return self.__resolveInkDash()
        try:
            ox = float(self.getX())
            oy = float(self.getY())
        except Exception:
            return Task.done
        hitRange, nearMiss = self.__hitRangesForMove('ink_splat')
        dmg = self.__damageForMove('ink_splat')
        now = globalClock.getFrameTime()  # noqa: F821
        anyHit = False
        anyDodge = False
        for target in self.__iterZoneToons():
            try:
                dx = float(target.getX()) - ox
                dy = float(target.getY()) - oy
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
            if self.__damageToonAndCheckReclaimKo(
                    target, dmg, context='ink_splat'):
                anyHit = True
        if anyHit:
            self.sendUpdate('announceAttackHit', [])
        elif anyDodge:
            self.sendUpdate('announceAttackDodged', [])
        return Task.done

    def __dashInkTowardTarget(self, target):
        """Planar dash step for ink_dash — short swarm rush toward the toon."""
        if target is None:
            return
        try:
            sx = float(self.getX())
            sy = float(self.getY())
            sz = float(self.getZ())
            tx = float(target.getX())
            ty = float(target.getY())
        except Exception:
            return
        dash = CorruptionGlobals.inkDashDist(self._stats)
        nx, ny = CorruptionGlobals.inkDashPos(sx, sy, tx, ty, dash=dash)
        if abs(nx - sx) < 1e-6 and abs(ny - sy) < 1e-6:
            return
        heading = -math.degrees(math.atan2(tx - sx, ty - sy))
        self.setPos(nx, ny, sz)
        self.setH(heading)
        self.sendUpdate('setXYZH', [nx, ny, sz, heading])

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
        self.__damageToonAndCheckReclaimKo(target, dmg, context='smack')
        # Balloon Snare: short planar reel toward the zip-flier (not damage-only).
        self.__yankTargetTowardSnare(target)
        # Corrupted Oswald: betrayal shove away (opposite Snare yank).
        self.__shoveTargetFromOswald(target)
        self.sendUpdate('announceAttackHit', [])
        return Task.done

    def __yankTargetTowardSnare(self, target):
        """Reel the hit toon a short distance toward this Balloon Snare.

        Server shadow displace so follow-up chase/hit math sees the yank.
        Client hurt-react lerp (hackslash) owns the readable local feel.
        No-op for non-Snare archetypes (Smudge / Brute / Oswald / Overlord).
        """
        if not getattr(CorruptionGlobals, 'SNARE_LASH_YANK_ENABLED', True):
            return
        if (CorruptionGlobals.normalizeArchetype(self.archetype)
                != CorruptionGlobals.ARCHETYPE_SNARE):
            return
        if target is None:
            return
        try:
            sx = float(self.getX())
            sy = float(self.getY())
            tx = float(target.getX())
            ty = float(target.getY())
            tz = float(target.getZ())
        except Exception:
            return
        nx, ny = CorruptionGlobals.snareLashYankPos(sx, sy, tx, ty)
        if abs(nx - tx) < 1e-6 and abs(ny - ty) < 1e-6:
            return
        try:
            target.setPos(nx, ny, tz)
        except Exception:
            self.notify.debug(
                'snare lash yank setPos failed on av %s' % getattr(
                    target, 'doId', self._targetId))

    def __shoveTargetFromOswald(self, target):
        """Knock the hit toon a short distance away from Corrupted Oswald.

        Betrayal identity — push away (opposite Balloon Snare yank). Server
        shadow displace so follow-up chase/hit math sees the shove. Client
        hurt-react lerp (hackslash) owns the readable local feel. No-op for
        non-Oswald archetypes or when the kit / shove is disabled.
        """
        if not getattr(CorruptionGlobals, 'OSWALD_BETRAYAL_KIT_ENABLED', True):
            return
        if not getattr(CorruptionGlobals, 'OSWALD_BETRAYAL_SHOVE_ENABLED', True):
            return
        if (CorruptionGlobals.normalizeArchetype(self.archetype)
                != CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD):
            return
        if target is None:
            return
        try:
            sx = float(self.getX())
            sy = float(self.getY())
            tx = float(target.getX())
            ty = float(target.getY())
            tz = float(target.getZ())
        except Exception:
            return
        dist = CorruptionGlobals.oswaldShoveDist(self._stats)
        nx, ny = CorruptionGlobals.oswaldBetrayalShovePos(
            sx, sy, tx, ty, dist=dist)
        if abs(nx - tx) < 1e-6 and abs(ny - ty) < 1e-6:
            return
        try:
            target.setPos(nx, ny, tz)
        except Exception:
            self.notify.debug(
                'oswald betrayal shove setPos failed on av %s' % getattr(
                    target, 'doId', self._targetId))

    def __defeat(self, attackerId=None):
        if self._defeated:
            return
        self._defeated = True
        self._attacking = False
        self._juggleHangStunUntil = 0.0
        self.__clearBruteSpitProjectile()
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
        self.__clearOverlordRainLinger()
        self.__clearBruteSpitProjectile()
        taskMgr.remove(self.uniqueName('corrupt-ai'))
        taskMgr.remove(self.uniqueName('corrupt-attack'))
        taskMgr.remove(self.uniqueName('corrupt-toon-delete'))
        DistributedNodeAI.delete(self)

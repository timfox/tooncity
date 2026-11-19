"""Soft nearest-hostile targeting for rubber-hose melee.

Prefers HackSlashTarget implementers (demo hostiles / CorruptToon),
then falls back to street suits as stand-ins for the prototype.

Includes manual soft-lock cycle (next/prev) so players can switch focus
among sticky-range hostiles during stretch-punch melee — KH-feel targeting
without KH branding / keyblades.

Auto-acquire (and fresh Tab with no lock) prefers Overlord/Oswald >
Elite > Ambush > nearer fodder (tiered rank, not binary). Sticky hold
yields when a strictly higher-tier subject enters the acquire cone so
climax/twist fights do not stay stuck on Elite/Ambush/trash. Manual
Tab/` with an existing lock jumps to Overlord/Oswald (or a higher tier)
in the cycle cone — a pack add jumps to Overlord/Oswald / Elite over
Ambush instead of yaw-orbiting through lower-tier hostiles.

Between-wave ambush also pulses soft-lock prefer on reclaimAmbushSpawn
(expire sticky glue) so mid-fight flanks steal focus immediately; Ambush
names stay permanent Ambush-tier priority via softLockPriorityTier
either way.
"""

import math

from . import HackSlashConfig

# Mirror CorruptionGlobals fodder tier for SoftTarget helpers when the
# corruption package is unavailable (headless SoftTarget-only loads).
_SOFT_LOCK_PRIORITY_TIER_FODDER = 3


def softLockAcquireRank(dist, priority=False):
    """Sort key for soft-lock acquire — lower wins.

    ``priority`` is either a bool (legacy binary: True → boss tier,
    False → fodder) or an int tier from softLockPriorityTier
    (Overlord/Oswald=0, Elite=1, Ambush=2, fodder=3). Nearest wins
    within the same tier. Pure helper for headless tests.
    """
    if isinstance(priority, bool):
        tier = 0 if priority else _SOFT_LOCK_PRIORITY_TIER_FODDER
    else:
        try:
            tier = int(priority)
        except (TypeError, ValueError):
            tier = _SOFT_LOCK_PRIORITY_TIER_FODDER
    return (tier, float(dist))


def isAmbushPreferName(name, prefix=None):
    """True when a hostile name is Ambush-prefixed for prefer pulse.

    Pure helper for headless tests. Prefers ReclaimGlobals.AMBUSH_NAME_PREFIX
    when available; falls back to ``'Ambush '``.
    """
    if prefix is None:
        try:
            from toontown.reclaim import ReclaimGlobals
            prefix = getattr(ReclaimGlobals, 'AMBUSH_NAME_PREFIX', 'Ambush ')
        except ImportError:
            prefix = 'Ambush '
    text = str(name or '')
    return bool(prefix) and text.startswith(str(prefix))


def ambushPreferWindowActive(preferUntil, now, enabled=None):
    """True while an ambush soft-lock prefer pulse window is live."""
    if enabled is None:
        enabled = getattr(
            HackSlashConfig, 'AMBUSH_SOFT_LOCK_PREFER_ENABLED', True)
    if not enabled:
        return False
    try:
        until = float(preferUntil or 0.0)
        t = float(now)
    except (TypeError, ValueError):
        return False
    return t < until


def pickSoftLockAcquire(scoredRows):
    """Pick best soft-lock candidate from scored rows.

    ``scoredRows`` is an iterable of ``(tier_or_priority, dist, payload)``.
    Empty input → None. Lower tier wins (boss > elite > ambush > fodder);
    nearest wins within a tier. Bool ``True``/``False`` still accepted as
    legacy binary priority.
    """
    best = None
    bestKey = None
    for row in scoredRows:
        if row is None or len(row) < 3:
            continue
        priority, dist, payload = row[0], row[1], row[2]
        key = softLockAcquireRank(dist, priority=priority)
        if bestKey is None or key < bestKey:
            bestKey = key
            best = payload
    return best


def shouldStickyYieldToPriority(
        lockedIsPriority, hasPriorityCandidate, enabled=None,
        lockedTier=None, candidateTier=None):
    """True when sticky hold should yield to a better-tier subject.

    Tier path (``lockedTier`` / ``candidateTier``): yield when the
    candidate tier is strictly lower (better) than the locked tier —
    Ambush sticky yields to Elite/Overlord; Elite yields to Overlord/
    Oswald; already on boss keeps sticky. Legacy binary path: yield
    only from fodder when any priority subject is in cone. Pure helper
    for headless tests.
    """
    if enabled is None:
        enabled = HackSlashConfig.TARGET_PRIORITY_ENABLED
    if not enabled:
        return False
    if lockedTier is not None:
        if candidateTier is None:
            return False
        try:
            return int(candidateTier) < int(lockedTier)
        except (TypeError, ValueError):
            return False
    if lockedIsPriority:
        return False
    return bool(hasPriorityCandidate)


def shouldCyclePreferPriority(
        lockedIsPriority, hasPriorityCandidate, enabled=None,
        lockedTier=None, candidateTier=None):
    """True when Tab/` with an existing lock should jump to a better tier.

    Tier path matches sticky yield: jump when a strictly higher-tier
    subject is in the cycle cone (Ambush → Elite/Overlord, Elite →
    Overlord/Oswald). Already on boss, or no better tier in cone →
    yaw-orbit. Legacy binary path: jump only from fodder. Pure helper
    for headless tests.
    """
    if enabled is None:
        enabled = HackSlashConfig.TARGET_PRIORITY_ENABLED
    if not enabled:
        return False
    if lockedTier is not None:
        if candidateTier is None:
            return False
        try:
            return int(candidateTier) < int(lockedTier)
        except (TypeError, ValueError):
            return False
    if lockedIsPriority:
        return False
    return bool(hasPriorityCandidate)


def nextCycleIndex(count, currentIndex, direction=1):
    """Return the next wraparound index for soft-lock target cycle.

    Pure helper (no Panda) so headless tests can cover cycle math.
    ``currentIndex`` may be None when nothing is locked yet — then we
    land on 0 for next / last for prev.
    """
    if count <= 0:
        return None
    step = 1 if int(direction) >= 0 else -1
    if currentIndex is None:
        return 0 if step > 0 else (count - 1)
    if count == 1:
        return 0
    return (int(currentIndex) + step) % count


def pickCycleChoice(orderedKeys, currentKey, direction=1):
    """Pick the next/prev key from an angle-sorted soft-lock candidate list.

    ``orderedKeys`` is already sorted (e.g. by signed yaw then distance).
    Returns (newKey, snapped) where snapped is True when the lock key
    actually changes. Empty list → (None, False). Sole matching lock →
    same key with snapped False (no juice spam).
    """
    if not orderedKeys:
        return None, False
    try:
        currentIndex = orderedKeys.index(currentKey) if currentKey in orderedKeys else None
    except (ValueError, TypeError):
        currentIndex = None
    newIndex = nextCycleIndex(len(orderedKeys), currentIndex, direction=direction)
    if newIndex is None:
        return None, False
    newKey = orderedKeys[newIndex]
    # First acquire onto a candidate counts as a snap; sole already-locked
    # target does not (avoids re-pop spam when only one hostile is in range).
    if currentIndex is None:
        snapped = newKey is not None
    else:
        snapped = newKey != currentKey
    return newKey, bool(snapped)


def signedYawDeltaDeg(fromYaw, toYaw):
    """Shortest signed yaw delta (degrees) from ``fromYaw`` to ``toYaw``.

    Result in [-180, 180). Pure helper so headless tests cover hit-assist math
    without Panda3D.
    """
    return ((float(toYaw) - float(fromYaw) + 180.0) % 360.0) - 180.0


def assistAimYawNudge(deltaDeg, frac=None, maxDeg=None, deadzoneDeg=None):
    """One-shot soft-lock hit-assist yaw nudge from a remaining facing error.

    Closes ``frac`` of ``deltaDeg``, hard-capped at ``maxDeg``, with a
    deadzone so already-aligned facing is left alone. Returns 0.0 when the
    error is tiny or tunables collapse the nudge. Never snaps to full delta
    unless frac/max allow it — soft assist, not hard lock.
    """
    if frac is None:
        frac = HackSlashConfig.LOCK_HIT_ASSIST_YAW_FRAC
    if maxDeg is None:
        maxDeg = HackSlashConfig.LOCK_HIT_ASSIST_YAW_MAX_DEG
    if deadzoneDeg is None:
        deadzoneDeg = HackSlashConfig.LOCK_HIT_ASSIST_DEADZONE_DEG
    delta = float(deltaDeg)
    if abs(delta) <= float(deadzoneDeg):
        return 0.0
    frac = max(0.0, float(frac))
    maxDeg = abs(float(maxDeg))
    nudge = delta * frac
    if nudge > maxDeg:
        return maxDeg
    if nudge < -maxDeg:
        return -maxDeg
    return nudge


def shouldAssistAimOnHit(hitKey, lockedKey, enabled=None):
    """True when a landed melee hit should fire soft-lock aim assist.

    Only when assist is enabled and the hit target matches the sticky
    soft-lock key — combo strings stay glued to the lock, not stray punches.
    """
    if enabled is None:
        enabled = HackSlashConfig.LOCK_HIT_ASSIST_ENABLED
    if not enabled:
        return False
    if hitKey is None or lockedKey is None:
        return False
    return hitKey == lockedKey


class HackSlashTarget:
    """Shared hit interface so melee and future CorruptToon enemies share a path."""

    def isHackSlashTarget(self):
        return True

    def isHackSlashAlive(self):
        raise NotImplementedError

    def getHackSlashHp(self):
        raise NotImplementedError

    def getHackSlashName(self):
        raise NotImplementedError

    def applyHackSlashHit(self, damage, hitIndex, attacker, counterFlags=0):
        """Apply damage / reaction. Return True if the hit landed."""
        raise NotImplementedError

    def getHackSlashPos(self):
        return self.getPos(render)  # noqa: F821


class SoftTargetFinder:
    """Pick the nearest living hostile in a forward cone, with brief lock hold."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._lockedKey = None
        self._lockedUntil = 0.0
        self._suitAdapters = {}
        # True only for the acquire() call that freshly snaps onto a target.
        self._snapped = False
        # reclaimAmbushSpawn prefer pulse — Ambush names score priority
        # while now < _ambushPreferUntil (sticky glue expires on pulse).
        self._ambushPreferUntil = 0.0

    def clear(self):
        self._lockedKey = None
        self._lockedUntil = 0.0
        self._suitAdapters.clear()
        self._snapped = False
        self._ambushPreferUntil = 0.0

    def pulseAmbushPrefer(self, duration=None, now=None):
        """Brief Ambush soft-lock prefer after reclaimAmbushSpawn.

        Expires sticky hold so the next acquire can snap onto Ambush-
        prefixed flanks. Returns True when the pulse armed.
        """
        if not getattr(
                HackSlashConfig, 'AMBUSH_SOFT_LOCK_PREFER_ENABLED', True):
            return False
        if now is None:
            try:
                now = float(globalClock.getFrameTime())  # noqa: F821
            except Exception:
                now = 0.0
        if duration is None:
            duration = getattr(
                HackSlashConfig, 'AMBUSH_SOFT_LOCK_PREFER_SEC', 4.0)
            try:
                from toontown.reclaim import ReclaimGlobals
                duration = getattr(
                    ReclaimGlobals, 'AMBUSH_SOFT_LOCK_PREFER_SEC', duration)
            except ImportError:
                pass
        try:
            hold = max(0.1, float(duration))
        except (TypeError, ValueError):
            hold = 4.0
        self._ambushPreferUntil = float(now) + hold
        # Drop sticky glue so mid-fight flanks can steal focus.
        self._lockedUntil = 0.0
        return True

    def isAmbushPreferActive(self, now=None):
        """True while the ambush soft-lock prefer pulse window is live."""
        if now is None:
            try:
                now = float(globalClock.getFrameTime())  # noqa: F821
            except Exception:
                now = 0.0
        return ambushPreferWindowActive(self._ambushPreferUntil, now)

    def didSnap(self):
        """True if the most recent acquire() snapped onto a new lock key."""
        return bool(self._snapped)

    def getLockedKey(self):
        return self._lockedKey

    def cycle(self, direction=1, now=None):
        """Manually switch soft-lock to the next/prev sticky-range hostile.

        Candidates are ordered by signed yaw around the avatar (then
        distance) so Tab/` reads as orbiting focus, not a random hop.
        Sets ``_snapped`` when the lock key changes so MeleeCombat can fire
        the brief cycle reticle pulse (not full acquire snap FOV/wash).
        """
        if now is None:
            now = globalClock.getFrameTime()  # noqa: F821

        self._snapped = False
        scored = []
        byKey = {}
        for target in self._iterCandidates():
            if not self._isValid(target):
                continue
            if not self._inCone(
                    target,
                    rangeLimit=HackSlashConfig.TARGET_CYCLE_RANGE,
                    halfAngle=HackSlashConfig.TARGET_CYCLE_HALF_ANGLE_DEG):
                continue
            key = self._key(target)
            byKey[key] = target
            scored.append((self._signedAngleDeg(target), self._distance(target), key))

        if not scored:
            self._lockedKey = None
            self._lockedUntil = 0.0
            return None

        scored.sort(key=lambda row: (row[0], row[1], str(row[2])))
        orderedKeys = [row[2] for row in scored]
        # Fresh Tab with nothing locked: land on preferred sticky hostile
        # (Overlord/Oswald > Elite > Ambush > fodder; direction still used
        # once a lock exists for orbit next/prev when not jumping tiers).
        if self._lockedKey not in byKey:
            ranked = []
            for yaw, dist, key in scored:
                target = byKey.get(key)
                ranked.append((
                    self._priorityTier(target),
                    dist,
                    key))
            newKey = pickSoftLockAcquire(ranked)
            snapped = newKey is not None
        else:
            # Locked path: jump to a strictly higher tier (Ambush→Elite/
            # Overlord, Elite→Overlord/Oswald, fodder→any prefer) over
            # yaw-orbit. Already on boss, or no better tier in cone →
            # normal pickCycleChoice.
            lockedTarget = byKey.get(self._lockedKey)
            lockedTier = self._priorityTier(lockedTarget)
            lockedIsPriority = self._isPriorityTarget(lockedTarget)
            higherRanked = []
            candidateTier = None
            for yaw, dist, key in scored:
                if key == self._lockedKey:
                    continue
                target = byKey.get(key)
                tier = self._priorityTier(target)
                if tier < lockedTier:
                    higherRanked.append((tier, dist, key))
                    if candidateTier is None or tier < candidateTier:
                        candidateTier = tier
            if shouldCyclePreferPriority(
                    lockedIsPriority, bool(higherRanked),
                    lockedTier=lockedTier,
                    candidateTier=candidateTier):
                newKey = pickSoftLockAcquire(higherRanked)
                snapped = newKey is not None and newKey != self._lockedKey
            else:
                newKey, snapped = pickCycleChoice(
                    orderedKeys, self._lockedKey, direction=direction)
        chosen = byKey.get(newKey) if newKey is not None else None
        self._lockedKey = newKey
        self._lockedUntil = (
            now + HackSlashConfig.TARGET_LOCK_HOLD_SEC if chosen is not None else 0.0)
        self._snapped = bool(snapped and chosen is not None)
        return chosen

    def acquire(self, now=None):
        if now is None:
            now = globalClock.getFrameTime()  # noqa: F821

        self._snapped = False
        prevKey = self._lockedKey
        candidates = list(self._iterCandidates())
        byKey = {self._key(t): t for t in candidates}

        # Sticky soft-lock: keep the current target while alive and roughly
        # in front / in sticky range (wider than fresh acquisition cone).
        # Yield sticky glue when a strictly higher-tier subject is already
        # in the fresh-acquire cone (Ambush→Elite/Overlord, Elite→
        # Overlord/Oswald, fodder→any prefer) so climax/twist do not stay
        # stuck on lower-tier hostiles after tiered soft-lock prefer.
        if self._lockedKey is not None and now < self._lockedUntil:
            locked = byKey.get(self._lockedKey)
            if locked is not None and self._isValid(locked) and self._inStickyCone(locked):
                lockedTier = self._priorityTier(locked)
                lockedIsPriority = self._isPriorityTarget(locked)
                candidateTier = None
                for target in candidates:
                    if self._key(target) == self._lockedKey:
                        continue
                    if not self._isValid(target):
                        continue
                    if not self._inCone(target):
                        continue
                    tier = self._priorityTier(target)
                    if candidateTier is None or tier < candidateTier:
                        candidateTier = tier
                hasPriorityCandidate = (
                    candidateTier is not None
                    and candidateTier < lockedTier)
                if not shouldStickyYieldToPriority(
                        lockedIsPriority, hasPriorityCandidate,
                        lockedTier=lockedTier,
                        candidateTier=candidateTier):
                    # Refresh hold while the target remains sticky-valid.
                    self._lockedUntil = now + HackSlashConfig.TARGET_LOCK_HOLD_SEC
                    return locked
                # Fall through to fresh tier scoring (snap onto better tier).
            else:
                self._lockedKey = None

        scored = []
        for target in candidates:
            if not self._isValid(target):
                continue
            if not self._inCone(target):
                continue
            scored.append((
                self._priorityTier(target),
                self._distance(target),
                target))
        best = pickSoftLockAcquire(scored)

        newKey = self._key(best) if best is not None else None
        self._lockedKey = newKey
        self._lockedUntil = now + HackSlashConfig.TARGET_LOCK_HOLD_SEC
        # Snap = first lock or switch onto a different living hostile.
        self._snapped = newKey is not None and newKey != prevKey
        return best

    def _priorityTier(self, target):
        """Soft-lock prefer tier for ``target`` — lower wins.

        Delegates to CorruptionGlobals.softLockPriorityTier (Overlord/
        Oswald > Elite > Ambush > fodder). reclaimAmbushSpawn pulse keeps
        Ambush names on the Ambush tier while sticky glue expires.
        """
        fodder = _SOFT_LOCK_PRIORITY_TIER_FODDER
        if target is None:
            return fodder
        if not getattr(HackSlashConfig, 'TARGET_PRIORITY_ENABLED', True):
            return fodder
        name = ''
        try:
            if callable(getattr(target, 'getHackSlashName', None)):
                name = str(target.getHackSlashName() or '')
            elif callable(getattr(target, 'getName', None)):
                name = str(target.getName() or '')
            else:
                name = str(getattr(target, 'name', '') or '')
        except Exception:
            name = ''
        try:
            from toontown.corruption import CorruptionGlobals
            fodder = int(getattr(
                CorruptionGlobals, 'SOFT_LOCK_PRIORITY_TIER_FODDER', fodder))
            ambushTier = int(getattr(
                CorruptionGlobals, 'SOFT_LOCK_PRIORITY_TIER_AMBUSH', 2))
        except ImportError:
            CorruptionGlobals = None
            ambushTier = 2
        # Brief ambush prefer pulse — sticky expire + Ambush flank boost
        # on reclaimAmbushSpawn. Permanent Ambush tier also lives in
        # softLockPriorityTier below (always-on name prefixes).
        if CorruptionGlobals is None:
            if self.isAmbushPreferActive() and isAmbushPreferName(name):
                return ambushTier
            return fodder
        archetype = 0
        finalePhase = 0
        try:
            if callable(getattr(target, 'getArchetype', None)):
                archetype = int(target.getArchetype())
            elif hasattr(target, 'archetype'):
                archetype = int(getattr(target, 'archetype', 0) or 0)
        except Exception:
            archetype = 0
        # Per-hostile phase only (AI Overlord DOs). Never use reclaim-director
        # street phase — P2 Smudge adds share that street flag.
        try:
            finalePhase = int(getattr(target, 'finalePhase', 0) or 0)
        except Exception:
            finalePhase = 0
        try:
            return int(CorruptionGlobals.softLockPriorityTier(
                archetype, name=name, finalePhase=finalePhase))
        except Exception:
            return fodder

    def _isPriorityTarget(self, target):
        """True for Overlord / Oswald / Elite / Ambush soft-lock preference.

        Permanent prefer comes from CorruptionGlobals.softLockPriorityTier
        (any non-fodder tier via isSoftLockPrioritySubject). reclaimAmbushSpawn
        also arms a brief Ambush prefer pulse that expires sticky glue so
        mid-fight flanks can steal focus immediately.
        """
        fodder = _SOFT_LOCK_PRIORITY_TIER_FODDER
        try:
            from toontown.corruption import CorruptionGlobals
            fodder = int(getattr(
                CorruptionGlobals, 'SOFT_LOCK_PRIORITY_TIER_FODDER', fodder))
        except ImportError:
            pass
        return self._priorityTier(target) < fodder

    def _key(self, target):
        if target is None:
            return None
        if hasattr(target, 'doId'):
            return ('doId', target.doId)
        if isinstance(target, SuitHackSlashAdapter):
            return ('suit', getattr(target.suit, 'doId', id(target.suit)))
        return ('id', id(target))

    def _iterCandidates(self):
        seen = set()

        # Prefer live CorruptToon / HackSlashTarget DOs over local demo dummies.
        for obj in list(getattr(base.cr, 'doId2do', {}).values()):  # noqa: F821
            if obj is self.avatar:
                continue
            if isinstance(obj, HackSlashTarget):
                key = self._key(obj)
                if key not in seen:
                    seen.add(key)
                    yield obj
            elif callable(getattr(obj, 'isHackSlashTarget', None)) and obj.isHackSlashTarget():
                key = self._key(obj)
                if key not in seen:
                    seen.add(key)
                    yield obj

        hostiles = getattr(self.avatar, 'hackSlashDemoHostiles', None) or []
        for hostile in hostiles:
            if hostile is not None:
                key = self._key(hostile)
                if key not in seen:
                    seen.add(key)
                    yield hostile

        # Street suits as stand-in hostiles when no corrupt toons are present.
        try:
            from toontown.suit.DistributedSuitBase import DistributedSuitBase
        except ImportError:
            DistributedSuitBase = None

        if DistributedSuitBase is not None:
            liveSuitIds = set()
            for obj in list(base.cr.doId2do.values()):  # noqa: F821
                if isinstance(obj, DistributedSuitBase):
                    liveSuitIds.add(obj.doId)
                    adapter = self._suitAdapters.get(obj.doId)
                    if adapter is None or adapter.suit is not obj:
                        adapter = SuitHackSlashAdapter(obj)
                        self._suitAdapters[obj.doId] = adapter
                    key = self._key(adapter)
                    if key not in seen:
                        seen.add(key)
                        yield adapter
            for doId in list(self._suitAdapters.keys()):
                if doId not in liveSuitIds:
                    del self._suitAdapters[doId]

    def _isValid(self, target):
        try:
            if hasattr(target, 'isHackSlashAlive'):
                return bool(target.isHackSlashAlive())
            return True
        except Exception:
            return False

    def _distance(self, target):
        return (self._pos(target) - self.avatar.getPos(render)).length()  # noqa: F821

    def _pos(self, target):
        if hasattr(target, 'getHackSlashPos'):
            return target.getHackSlashPos()
        return target.getPos(render)  # noqa: F821

    def _inCone(self, target, rangeLimit=None, halfAngle=None):
        toTarget = self._pos(target) - self.avatar.getPos(render)  # noqa: F821
        toTarget.setZ(0)
        dist = toTarget.length()
        if rangeLimit is None:
            rangeLimit = HackSlashConfig.TARGET_RANGE
        if halfAngle is None:
            halfAngle = HackSlashConfig.TARGET_HALF_ANGLE_DEG
        if dist < 0.01 or dist > rangeLimit:
            return False

        forward = self.avatar.getQuat(render).getForward()  # noqa: F821
        forward.setZ(0)
        if forward.length() < 0.01:
            return True
        forward.normalize()
        toTarget.normalize()
        dot = max(-1.0, min(1.0, forward.dot(toTarget)))
        angle = math.degrees(math.acos(dot))
        return angle <= halfAngle

    def _inStickyCone(self, target):
        return self._inCone(
            target,
            rangeLimit=HackSlashConfig.TARGET_STICKY_RANGE,
            halfAngle=HackSlashConfig.TARGET_STICKY_HALF_ANGLE_DEG)

    def _signedAngleDeg(self, target):
        """Signed yaw (degrees) from avatar forward to target on the XY plane.

        Negative = left, positive = right. Used to order soft-lock cycle
        candidates so next/prev orbit around Oswald.
        """
        toTarget = self._pos(target) - self.avatar.getPos(render)  # noqa: F821
        toTarget.setZ(0)
        if toTarget.length() < 0.01:
            return 0.0
        toTarget.normalize()
        forward = self.avatar.getQuat(render).getForward()  # noqa: F821
        forward.setZ(0)
        if forward.length() < 0.01:
            return 0.0
        forward.normalize()
        crossZ = forward.getX() * toTarget.getY() - forward.getY() * toTarget.getX()
        dot = max(-1.0, min(1.0, forward.dot(toTarget)))
        return math.degrees(math.atan2(crossZ, dot))


class SuitHackSlashAdapter(HackSlashTarget):
    """Thin adapter so existing street suits can be soft-targeted in the demo."""

    def __init__(self, suit):
        self.suit = suit
        self._stubHp = 30

    def isHackSlashTarget(self):
        return True

    def isHackSlashAlive(self):
        suit = self.suit
        if suit is None:
            return False
        try:
            if suit.isEmpty():
                return False
        except Exception:
            pass
        return self._stubHp > 0

    def getHackSlashHp(self):
        return self._stubHp

    def getHackSlashName(self):
        try:
            return self.suit.getName()
        except Exception:
            return 'Suit'

    def getHackSlashPos(self):
        return self.suit.getPos(render)  # noqa: F821

    def applyHackSlashHit(self, damage, hitIndex, attacker, counterFlags=0):
        if not self.isHackSlashAlive():
            return False
        self._stubHp = max(0, self._stubHp - damage)
        suit = self.suit
        try:
            suit.play('lunge')
        except Exception:
            try:
                suit.play('walk')
            except Exception:
                pass
        try:
            away = suit.getPos(render) - attacker.getPos(render)  # noqa: F821
            away.setZ(0)
            if away.length() > 0.01:
                away.normalize()
                suit.setPos(suit.getPos() + away * (0.6 + 0.25 * hitIndex))
        except Exception:
            pass
        return True

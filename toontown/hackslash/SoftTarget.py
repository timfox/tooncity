"""Soft nearest-hostile targeting for rubber-hose melee.

Prefers HackSlashTarget implementers (demo hostiles / CorruptToon),
then falls back to street suits as stand-ins for the prototype.

Includes manual soft-lock cycle (next/prev) so players can switch focus
among sticky-range hostiles during stretch-punch melee — KH-feel targeting
without KH branding / keyblades.

Auto-acquire (and fresh Tab with no lock) prefers Ink Overlord /
Corrupted Oswald over nearer pack Smudge adds. Sticky hold also yields
from glued adds when a priority Overlord/Oswald enters the acquire cone
so climax and twist fights do not stay stuck on trash.
"""

import math

from . import HackSlashConfig


def softLockAcquireRank(dist, priority=False):
    """Sort key for soft-lock acquire — lower wins.

    Priority subjects (Overlord / Corrupted Oswald) sort before pack adds;
    nearest wins within the same tier. Pure helper for headless tests.
    """
    return (0 if priority else 1, float(dist))


def pickSoftLockAcquire(scoredRows):
    """Pick best soft-lock candidate from scored rows.

    ``scoredRows`` is an iterable of ``(priority, dist, payload)``. Empty
    input → None. Priority beats non-priority; nearest wins within a tier.
    """
    best = None
    bestKey = None
    for row in scoredRows:
        if row is None or len(row) < 3:
            continue
        priority, dist, payload = row[0], row[1], row[2]
        key = softLockAcquireRank(dist, priority=bool(priority))
        if bestKey is None or key < bestKey:
            bestKey = key
            best = payload
    return best


def shouldStickyYieldToPriority(
        lockedIsPriority, hasPriorityCandidate, enabled=None):
    """True when sticky hold on a pack add should yield to Overlord/Oswald.

    Sticky still glues onto the current target when already on a priority
    subject, when no priority candidate is in the acquire cone, or when
    TARGET_PRIORITY_ENABLED is off. Pure helper for headless tests.
    """
    if enabled is None:
        enabled = HackSlashConfig.TARGET_PRIORITY_ENABLED
    if not enabled:
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

    def applyHackSlashHit(self, damage, hitIndex, attacker):
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

    def clear(self):
        self._lockedKey = None
        self._lockedUntil = 0.0
        self._suitAdapters.clear()
        self._snapped = False

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
        # (Overlord / Oswald over nearer pack adds; direction still used
        # once a lock exists for orbit next/prev).
        if self._lockedKey not in byKey:
            ranked = []
            for yaw, dist, key in scored:
                target = byKey.get(key)
                ranked.append((
                    self._isPriorityTarget(target),
                    dist,
                    key))
            newKey = pickSoftLockAcquire(ranked)
            snapped = newKey is not None
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
        # Yield sticky glue on pack adds when Overlord / Corrupted Oswald is
        # already in the fresh-acquire cone so climax/twist do not stay
        # stuck on Smudge trash after #339 fresh-acquire priority.
        if self._lockedKey is not None and now < self._lockedUntil:
            locked = byKey.get(self._lockedKey)
            if locked is not None and self._isValid(locked) and self._inStickyCone(locked):
                lockedIsPriority = self._isPriorityTarget(locked)
                hasPriorityCandidate = False
                if not lockedIsPriority:
                    for target in candidates:
                        if self._key(target) == self._lockedKey:
                            continue
                        if not self._isValid(target):
                            continue
                        if not self._inCone(target):
                            continue
                        if self._isPriorityTarget(target):
                            hasPriorityCandidate = True
                            break
                if not shouldStickyYieldToPriority(
                        lockedIsPriority, hasPriorityCandidate):
                    # Refresh hold while the target remains sticky-valid.
                    self._lockedUntil = now + HackSlashConfig.TARGET_LOCK_HOLD_SEC
                    return locked
                # Fall through to fresh priority scoring (snap onto boss).
            else:
                self._lockedKey = None

        scored = []
        for target in candidates:
            if not self._isValid(target):
                continue
            if not self._inCone(target):
                continue
            scored.append((
                self._isPriorityTarget(target),
                self._distance(target),
                target))
        best = pickSoftLockAcquire(scored)

        newKey = self._key(best) if best is not None else None
        self._lockedKey = newKey
        self._lockedUntil = now + HackSlashConfig.TARGET_LOCK_HOLD_SEC
        # Snap = first lock or switch onto a different living hostile.
        self._snapped = newKey is not None and newKey != prevKey
        return best

    def _isPriorityTarget(self, target):
        """True for Ink Overlord / Corrupted Oswald soft-lock preference."""
        if target is None:
            return False
        if not getattr(HackSlashConfig, 'TARGET_PRIORITY_ENABLED', True):
            return False
        try:
            from toontown.corruption import CorruptionGlobals
        except ImportError:
            return False
        archetype = 0
        name = ''
        finalePhase = 0
        try:
            if callable(getattr(target, 'getArchetype', None)):
                archetype = int(target.getArchetype())
            elif hasattr(target, 'archetype'):
                archetype = int(getattr(target, 'archetype', 0) or 0)
        except Exception:
            archetype = 0
        try:
            if callable(getattr(target, 'getHackSlashName', None)):
                name = str(target.getHackSlashName() or '')
            elif callable(getattr(target, 'getName', None)):
                name = str(target.getName() or '')
            else:
                name = str(getattr(target, 'name', '') or '')
        except Exception:
            name = ''
        # Per-hostile phase only (AI Overlord DOs). Never use reclaim-director
        # street phase — P2 Smudge adds share that street flag.
        try:
            finalePhase = int(getattr(target, 'finalePhase', 0) or 0)
        except Exception:
            finalePhase = 0
        try:
            return bool(CorruptionGlobals.isSoftLockPrioritySubject(
                archetype, name=name, finalePhase=finalePhase))
        except Exception:
            return False

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

    def applyHackSlashHit(self, damage, hitIndex, attacker):
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

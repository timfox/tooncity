"""Soft nearest-hostile targeting for rubber-hose melee.

Prefers HackSlashTarget implementers (demo hostiles / CorruptToon),
then falls back to street suits as stand-ins for the prototype.
"""

import math

from . import HackSlashConfig


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

    def acquire(self, now=None):
        if now is None:
            now = globalClock.getFrameTime()  # noqa: F821

        self._snapped = False
        prevKey = self._lockedKey
        candidates = list(self._iterCandidates())
        byKey = {self._key(t): t for t in candidates}

        # Sticky soft-lock: keep the current target while alive and roughly
        # in front / in sticky range (wider than fresh acquisition cone).
        if self._lockedKey is not None and now < self._lockedUntil:
            locked = byKey.get(self._lockedKey)
            if locked is not None and self._isValid(locked) and self._inStickyCone(locked):
                # Refresh hold while the target remains sticky-valid.
                self._lockedUntil = now + HackSlashConfig.TARGET_LOCK_HOLD_SEC
                return locked
            self._lockedKey = None

        best = None
        bestDist = HackSlashConfig.TARGET_RANGE
        for target in candidates:
            if not self._isValid(target):
                continue
            if not self._inCone(target):
                continue
            dist = self._distance(target)
            if dist < bestDist:
                bestDist = dist
                best = target

        newKey = self._key(best) if best is not None else None
        self._lockedKey = newKey
        self._lockedUntil = now + HackSlashConfig.TARGET_LOCK_HOLD_SEC
        # Snap = first lock or switch onto a different living hostile.
        self._snapped = newKey is not None and newKey != prevKey
        return best

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

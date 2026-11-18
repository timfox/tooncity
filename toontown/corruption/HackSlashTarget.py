"""Shared melee-target interface for corrupt toons (and future hostiles).

Slice 1 soft-lock / hit events should prefer objects that expose this API so
combat and corruption can merge without turn-based cog battles.
"""


class HackSlashTarget:
    """Mixin / duck-typed contract for real-time melee targets."""

    def isHackSlashTarget(self):
        return True

    def getHackSlashHp(self):
        return getattr(self, 'hp', 0)

    def getHackSlashMaxHp(self):
        return getattr(self, 'maxHp', 0)

    def isHackSlashAlive(self):
        return self.getHackSlashHp() > 0

    def takeHackSlashDamage(self, amount, attackerId=None):
        """Apply damage. AI subclasses should override and sync state."""
        raise NotImplementedError

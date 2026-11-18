"""Shared melee-target interface for corrupt toons (and future hostiles).

Slice 1 SoftTarget prefers objects that expose this API. MeleeCombat calls
`applyHackSlashHit` on the client; CorruptToon bridges that to AI via
`requestHackSlashHit(hitIndex, counterFlags)` → authoritative
`meleeDamageFromHitIndex` / `takeHackSlashDamage` (+ juggle-hang stun on
launch beats so AI chase/attack pause during hang). Client damage is juice
only — the AI owns the COMBO_DAMAGE table.
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

    def getHackSlashName(self):
        return getattr(self, 'name', 'Hostile')

    def takeHackSlashDamage(self, amount, attackerId=None):
        """Apply damage. AI subclasses should override and sync state."""
        raise NotImplementedError

    def applyHackSlashHit(self, damage, hitIndex, attacker, counterFlags=0):
        """Client hit bridge used by MeleeCombat SoftTarget resolution."""
        raise NotImplementedError

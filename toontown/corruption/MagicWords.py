"""Corruption magic words — registered via MagicWordIndex import.

Keep this file as the only home for pollute / purify / spawncorrupt so the
parallel melee PR can own its own MagicWordIndex touch without merge fights.
"""

import math

from toontown.spellbook import MagicWordConfig
from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.corruption import CorruptionGlobals
from toontown.corruption.DistributedCorruptToonAI import DistributedCorruptToonAI


class Pollute(MagicWord):
    aliases = ['pollution', 'corruptzone']
    desc = 'Raise pollution in the invoker zone (0..1 pure to polluted).'
    advancedDesc = (
        'Sets or bumps per-zone pollution via PollutionManager. '
        'Omit amount to step by %.2f. Use absolute=1 to set exactly.'
        % CorruptionGlobals.POLLUTION_STEP_DEFAULT)
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('amount', float, False, CorruptionGlobals.POLLUTION_STEP_DEFAULT),
        ('absolute', int, False, 0),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        amount = float(args[0]) if args else CorruptionGlobals.POLLUTION_STEP_DEFAULT
        absolute = int(args[1]) if len(args) > 1 else 0
        mgr = getattr(self.air, 'pollutionManager', None)
        if mgr is None:
            return 'PollutionManager is not running on this AI.'
        zoneId = toon.zoneId
        if absolute:
            level = mgr.setPollution(zoneId, amount)
            return 'Zone %s pollution set to %.3f.' % (zoneId, level)
        level = mgr.adjustPollution(zoneId, abs(amount))
        return 'Zone %s pollution raised to %.3f.' % (zoneId, level)


class Purify(MagicWord):
    aliases = ['cleanzone', 'reclaim']
    desc = 'Lower pollution in the invoker zone toward pure (0).'
    advancedDesc = (
        'Reduces per-zone pollution. Omit amount to step by %.2f. '
        'Use absolute=1 to set exactly (0 fully purifies).'
        % CorruptionGlobals.POLLUTION_STEP_DEFAULT)
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('amount', float, False, CorruptionGlobals.POLLUTION_STEP_DEFAULT),
        ('absolute', int, False, 0),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        amount = float(args[0]) if args else CorruptionGlobals.POLLUTION_STEP_DEFAULT
        absolute = int(args[1]) if len(args) > 1 else 0
        mgr = getattr(self.air, 'pollutionManager', None)
        if mgr is None:
            return 'PollutionManager is not running on this AI.'
        zoneId = toon.zoneId
        if absolute:
            level = mgr.setPollution(zoneId, amount)
        else:
            level = mgr.adjustPollution(zoneId, -abs(amount))
        if level <= CorruptionGlobals.POLLUTION_PURE:
            return 'Zone %s fully purified (0.000).' % zoneId
        return 'Zone %s pollution lowered to %.3f.' % (zoneId, level)


class SpawnCorrupt(MagicWord):
    aliases = ['spawncorrupttoon', 'corrupttoon', 'spawnct', 'spawnbrute']
    desc = 'Spawn CorruptToon enemies (Ink Smudge or Sludge Brute).'
    advancedDesc = (
        'Generates DistributedCorruptToonAI in the invoker zone. '
        'Client prefers DNA/Actor ink silhouette, else card limbs. '
        'Ink Smudge: purple melee telegraph + impact flash/thud. '
        'Sludge Brute (archetype=1): green spit telegraph/SFX + ink blob. '
        'Optional count (1-8), hp, archetype (0=Ink, 1=Brute). '
        'Defeat lowers zone pollution. Pair with ~hackslash 0 for melee.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('count', int, False, 1),
        ('hp', int, False, CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP),
        ('archetype', int, False, CorruptionGlobals.ARCHETYPE_INK),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        count = int(args[0]) if args else 1
        hp = int(args[1]) if len(args) > 1 else CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
        archetype = (
            int(args[2]) if len(args) > 2
            else CorruptionGlobals.ARCHETYPE_INK)
        count = max(1, min(8, count))
        hp = max(1, min(500, hp))
        if archetype not in (
                CorruptionGlobals.ARCHETYPE_INK,
                CorruptionGlobals.ARCHETYPE_BRUTE):
            archetype = CorruptionGlobals.ARCHETYPE_INK
        stats = CorruptionGlobals.archetypeStats(archetype)

        zoneId = toon.zoneId
        baseX, baseY, baseZ = toon.getX(), toon.getY(), toon.getZ()
        heading = toon.getH()
        spawned = []
        for i in range(count):
            corrupt = DistributedCorruptToonAI(
                self.air, maxHp=hp, archetype=archetype)
            corrupt.hp = corrupt.maxHp
            # Fan out a few feet in front of the toon.
            offset = 6.0 + (i * 2.5)
            rad = math.radians(heading)
            x = baseX - math.sin(rad) * offset
            y = baseY + math.cos(rad) * offset
            corrupt.setPos(x, y, baseZ)
            corrupt.setH(heading + 180.0)
            corrupt.generateWithRequired(zoneId)
            spawned.append(corrupt.doId)

        return 'Spawned %s %s(s) in zone %s: %s' % (
            len(spawned), stats.get('name', 'CorruptToon'), zoneId, spawned)


def registerCorruptionMagicWords():
    """Instantiate word classes so they register into magicWordIndex."""
    Pollute()
    Purify()
    SpawnCorrupt()

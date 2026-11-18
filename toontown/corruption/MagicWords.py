"""Corruption magic words — registered via MagicWordIndex import.

Keep this file as the only home for pollute / purify / spawncorrupt so the
parallel melee PR can own its own MagicWordIndex touch without merge fights.
"""

import math

from toontown.spellbook import MagicWordConfig
from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.corruption import CorruptionGlobals
from toontown.corruption.DistributedCorruptToonAI import DistributedCorruptToonAI


def _spawnCorruptPack(air, toon, count=1, hpArg=0, archetype=None,
                      finalePhase=0):
    """Shared spawn helper for SpawnCorrupt / SpawnOverlord magic words."""
    if archetype is None:
        archetype = CorruptionGlobals.ARCHETYPE_INK
    archetype = CorruptionGlobals.normalizeArchetype(archetype)
    count = max(1, min(8, int(count)))
    # Pass base HP; DistributedCorruptToonAI applies archetype hpScale.
    if int(hpArg) <= 0:
        hp = CorruptionGlobals.archetypeDefaultHp(archetype)
    else:
        hp = max(1, min(500, int(hpArg)))
    finalePhase = CorruptionGlobals.normalizeFinalePhase(finalePhase)
    stats = CorruptionGlobals.archetypeStats(archetype)
    combat = CorruptionGlobals.overlordPhaseCombat(finalePhase)
    if combat:
        name = (
            'Ink Overlord Unleashed' if finalePhase >= 2
            else 'Ink Overlord')
    else:
        name = stats.get('name', 'CorruptToon')

    zoneId = toon.zoneId
    baseX, baseY, baseZ = toon.getX(), toon.getY(), toon.getZ()
    heading = toon.getH()
    spawned = []
    for i in range(count):
        spawnName = name if count == 1 else '%s %s' % (name, i + 1)
        corrupt = DistributedCorruptToonAI(
            air, name=spawnName, maxHp=hp, archetype=archetype,
            finalePhase=finalePhase)
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

    phaseTag = ''
    if finalePhase >= 1:
        phaseTag = ' finalePhase=%s (%s)' % (
            finalePhase, combat.get('id') if combat else '?')
    return 'Spawned %s %s(s) in zone %s%s: %s' % (
        len(spawned), name, zoneId, phaseTag, spawned)


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
        if (hasattr(mgr, 'isPurityLocked') and mgr.isPurityLocked(zoneId)
                and getattr(CorruptionGlobals, 'STREET_PURITY_LOCK_ENABLED', True)):
            return (
                'Zone %s is purity-locked after reclaim — ink can't creep back. '
                'Start a reclaim (~startreclaim) to unlock.' % zoneId)
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
    aliases = [
        'spawncorrupttoon', 'corrupttoon', 'spawnct',
        'spawnbrute', 'spawnsnare', 'spawnballoon',
    ]
    desc = 'Spawn CorruptToon enemies (Smudge, Brute, Snare, Gagster, Overlord).'
    advancedDesc = (
        'Generates DistributedCorruptToonAI in the invoker zone. '
        'Optional count (1-8), hp (0=archetype default base), '
        'archetype (0=Ink, 1=Brute, 2=Snare, 3=Gagster), finalePhase '
        '(0=street, 1=Overlord P1 rain AoE, 2=Unleashed rain+slam). '
        'Use ~spawngagster / ~spawnoverlord for shortcuts. '
        'Defeat lowers zone pollution. Pair with ~hackslash 0 for melee.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('count', int, False, 1),
        ('hp', int, False, 0),
        ('archetype', int, False, CorruptionGlobals.ARCHETYPE_INK),
        ('finalePhase', int, False, 0),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        count = int(args[0]) if args else 1
        hpArg = int(args[1]) if len(args) > 1 else 0
        archetype = (
            int(args[2]) if len(args) > 2
            else CorruptionGlobals.ARCHETYPE_INK)
        finalePhase = int(args[3]) if len(args) > 3 else 0
        return _spawnCorruptPack(
            self.air, toon, count=count, hpArg=hpArg, archetype=archetype,
            finalePhase=finalePhase)


class SpawnGagster(MagicWord):
    aliases = ['spawngagster', 'spawngunk', 'gunkgagster']
    desc = 'Spawn Gunk Gagster (teal gag-lob puddle archetype).'
    advancedDesc = (
        'Shortcut for ARCHETYPE_GAGSTER. Optional count, hp (0=default base). '
        'Gagsters lob a delayed teal puddle trap — dodge out during telegraph. '
        'Pair with ~hackslash 0.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('count', int, False, 1),
        ('hp', int, False, 0),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        count = int(args[0]) if args else 1
        hpArg = int(args[1]) if len(args) > 1 else 0
        return _spawnCorruptPack(
            self.air, toon, count=count, hpArg=hpArg,
            archetype=CorruptionGlobals.ARCHETYPE_GAGSTER)


class SpawnOverlord(MagicWord):
    aliases = ['spawnoverlord', 'spawninkoverlord', 'overlord']
    desc = 'Spawn Ink Overlord with phase combat AI (P1 rain / P2 enrage).'
    advancedDesc = (
        'Shortcut for Overlord phase AI. Optional count, hp (0=90 base), '
        'finalePhase (1=rising rain AoE, 2=unleashed rain+slam). '
        'Defaults to P1. Pair with ~hackslash 0.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('count', int, False, 1),
        ('hp', int, False, 90),
        ('finalePhase', int, False, 1),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        count = int(args[0]) if args else 1
        hpArg = int(args[1]) if len(args) > 1 else 90
        finalePhase = int(args[2]) if len(args) > 2 else 1
        return _spawnCorruptPack(
            self.air, toon, count=count, hpArg=hpArg,
            archetype=CorruptionGlobals.ARCHETYPE_INK,
            finalePhase=finalePhase)


def registerCorruptionMagicWords():
    """Instantiate word classes so they register into magicWordIndex."""
    Pollute()
    Purify()
    SpawnCorrupt()
    SpawnGagster()
    SpawnOverlord()

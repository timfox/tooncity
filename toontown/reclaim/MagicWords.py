"""Reclaim magic words — registered via MagicWordIndex import.

Keep ~startreclaim / ~stopreclaim here so MagicWordIndex only needs one line.
"""

from toontown.spellbook import MagicWordConfig
from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.reclaim import ReclaimGlobals
from toontown.reclaim.DistributedReclaimDirectorAI import DistributedReclaimDirectorAI


def _directors(air):
    directors = getattr(air, 'reclaimDirectors', None)
    if directors is None:
        directors = {}
        air.reclaimDirectors = directors
    return directors


class StartReclaim(MagicWord):
    aliases = ['startreclaim', 'reclaimstreet', 'beginreclaim']
    desc = 'Start the neighborhood reclaim loop in the invoker zone.'
    advancedDesc = (
        'Seeds partial pollution, spawns CorruptToon packs via ReclaimDirector, '
        'and drives purity restore when pollution hits 0 (cream wash pulse + '
        'delayed cream aftershock + soft cream wash pulse + street sparkle, '
        'FOV punch + soft FOV cream '
        'wash pulse, cheer pitch swell + cream '
        'flecks + delayed cream aftershock + soft cream wash pulse). Progressive '
        'street cream wash gets a delayed cream aftershock on purity advances. '
        'Polluted street entry cream wash gets a delayed cream aftershock + '
        'soft cream wash pulse. '
        'Purity meter fill shimmer gets a '
        'delayed cream aftershock + soft cream wash pulse. Wave-clear cream '
        'shimmer hang gets a '
        'delayed cream aftershock + soft cream wash pulse + deepened cream '
        'sparkle flecks (+ soft sparkle aftershock). Wave announce '
        'plates get a cream edge pulse with cream sparkle flecks + soft '
        'cream wash pulse, and the purity meter hose-pops briefly so wave '
        'begin reads clearly (sunny cream, not mid-wave rim flash or '
        'secured green lock). Mid-wave purity stall / ink-rise whispers a '
        'short contested tip under the purity meter and flashes the meter '
        'rim warm (danger blink, not the secured green lock). Full clear '
        'purity-locks the street so re-creep cannot undo it (HUD secured '
        'tip + green-cream sparkle sting), then after the purity '
        'celebration settles the meter hose-settles so the finish reads '
        'clearly (soft tall stretch, not wave-start squash or lock soft '
        'scale). Pair with '
        '~hackslash 0 for melee without demo dummies.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = []

    def handleWord(self, invoker, avId, toon, *args):
        zoneId = toon.zoneId
        directors = _directors(self.air)
        existing = directors.get(zoneId)
        if existing is not None and not existing.isDeleted():
            if existing.state == ReclaimGlobals.STATE_ACTIVE:
                return 'Reclaim already active in zone %s.' % zoneId
            existing.requestDelete()
            directors.pop(zoneId, None)

        director = DistributedReclaimDirectorAI(self.air, zoneId=zoneId)
        director.generateWithRequired(zoneId)
        directors[zoneId] = director
        packKwargs = ReclaimGlobals.streetPackParams(zoneId)
        director.start(
            zoneId,
            (toon.getX(), toon.getY(), toon.getZ()),
            toon.getH(),
            **packKwargs)
        pack = ReclaimGlobals.streetPack(zoneId) or {}
        packId = pack.get('packId') or 'default'
        seed = pack.get(
            'seedPollution', ReclaimGlobals.RECLAIM_START_POLLUTION)
        maxPacks = pack.get('maxPacks', ReclaimGlobals.MAX_PACKS)
        packSize = pack.get('packSize', ReclaimGlobals.PACK_SIZE)
        return (
            'Reclaim started in zone %s [%s] (pollution %.2f, %s escalating '
            'waves, base pack %s). Enable melee with ~hackslash 0, then '
            'clear waves.'
            % (zoneId, packId, seed, maxPacks, packSize))


class StopReclaim(MagicWord):
    aliases = ['stopreclaim', 'endreclaim', 'cancelreclaim']
    desc = 'Stop the active reclaim director in the invoker zone.'
    advancedDesc = (
        'Deletes spawned reclaim CorruptToons and clears director state. '
        'Bailing mid-reclaim marks the street contested so residual ink '
        'slowly re-creeps (pure / finished streets stay purity-locked).')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = []

    def handleWord(self, invoker, avId, toon, *args):
        zoneId = toon.zoneId
        directors = _directors(self.air)
        director = directors.get(zoneId)
        if director is None or director.isDeleted():
            directors.pop(zoneId, None)
            return 'No reclaim director in zone %s.' % zoneId
        director.stop()
        director.requestDelete()
        directors.pop(zoneId, None)
        return (
            'Reclaim stopped in zone %s — unfinished streets slowly re-ink!'
            % zoneId)


def registerReclaimMagicWords():
    """Instantiate word classes so they register into magicWordIndex."""
    StartReclaim()
    StopReclaim()

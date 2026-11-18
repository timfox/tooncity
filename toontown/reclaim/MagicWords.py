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
        'and drives purity restore when pollution hits 0. Pair with '
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
        director.start(
            zoneId,
            (toon.getX(), toon.getY(), toon.getZ()),
            toon.getH())
        return (
            'Reclaim started in zone %s (pollution %.2f, packs of %s). '
            'Enable melee with ~hackslash 0, then clear Corrupt Toons.'
            % (zoneId, ReclaimGlobals.RECLAIM_START_POLLUTION,
               ReclaimGlobals.PACK_SIZE))


class StopReclaim(MagicWord):
    aliases = ['stopreclaim', 'endreclaim', 'cancelreclaim']
    desc = 'Stop the active reclaim director in the invoker zone.'
    advancedDesc = 'Deletes spawned reclaim CorruptToons and clears director state.'
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
        return 'Reclaim stopped in zone %s.' % zoneId


def registerReclaimMagicWords():
    """Instantiate word classes so they register into magicWordIndex."""
    StartReclaim()
    StopReclaim()

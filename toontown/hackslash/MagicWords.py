"""Hack-slash magic words. Imported/registered from MagicWordIndex."""

from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.spellbook import MagicWordConfig


class ToggleHackSlash(MagicWord):
    aliases = ['hackslash', 'melee', 'rubberhose', 'khcombat']
    desc = 'Toggle real-time rubber-hose melee demo mode.'
    advancedDesc = (
        'Enables the KH-style hack-and-slash prototype: press F (or LMB) to '
        'swing a short 3-hit combo with soft nearest-hostile targeting, a '
        'subtle camera/facing nudge toward the sticky lock, hitstop, and a '
        'brief white flash on connect (finisher also FOV-punches). '
        'Spawns ink demo hostiles in front of you. Toggle again to disable. '
        'Does not use turn-based cog battles.'
    )
    execLocation = MagicWordConfig.EXEC_LOC_CLIENT
    arguments = [('spawn', int, False, 1)]

    def handleWord(self, invoker, avId, toon, *args):
        spawn = True
        if args:
            spawn = bool(args[0])
        # Always drive the local avatar — client-exec magic words run locally.
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None:
            return 'No local avatar.'
        if not hasattr(av, 'toggleHackSlashMelee'):
            return 'Local avatar missing hackslash hooks.'
        enabled = av.toggleHackSlashMelee(spawnHostiles=spawn)
        if enabled:
            return (
                'Hack-Slash demo ON. Press F (or LMB) for melee combos. '
                'Camera/facing nudge toward soft-lock; white flash on hit. '
                'Soft-targets demo hostiles (and street suits).'
            )
        return 'Hack-Slash demo OFF.'

"""Hack-slash magic words. Imported/registered from MagicWordIndex."""

from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.spellbook import MagicWordConfig


class ToggleHackSlash(MagicWord):
    aliases = ['hackslash', 'melee', 'rubberhose', 'khcombat']
    desc = 'Toggle real-time rubber-hose melee demo mode.'
    advancedDesc = (
        'Enables the KH-style hack-and-slash prototype: press F (or LMB) to '
        'swing a short 3-hit combo with soft nearest-hostile targeting, a '
        'subtle camera/facing nudge toward the sticky lock (mid-combo soft '
        'orbit/pull for readability without hard-locking), hitstop, a brief '
        'white flash on connect, and an on-screen combo counter that ticks '
        'on hits then fades when the string breaks (finisher also FOV-punches). '
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
                'Combo counter ticks on connect; soft-lock orbit mid-combo + '
                'hit flash. Soft-targets demo hostiles (and street suits).'
            )
        return 'Hack-Slash demo OFF.'

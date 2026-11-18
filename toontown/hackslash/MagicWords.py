"""Rubber-hose melee magic words. Imported/registered from MagicWordIndex."""

from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.spellbook import MagicWordConfig


class ToggleHackSlash(MagicWord):
    aliases = ['hackslash', 'melee', 'rubberhose', 'fists', 'stretchpunch']
    desc = 'Toggle real-time rubber-hose Oswald stretch-punch melee.'
    advancedDesc = (
        'Enables rubber-hose melee: press F (or LMB) for a short 3-hit stretch '
        'punch combo with soft nearest-hostile targeting, a subtle '
        'camera/facing nudge toward the sticky lock (mid-combo soft '
        'orbit/pull for readability without hard-locking), hitstop, a brief '
        'white flash on connect, and an on-screen punch counter that ticks '
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
            return 'Local avatar missing melee hooks.'
        enabled = av.toggleHackSlashMelee(spawnHostiles=spawn)
        if enabled:
            return (
                'Stretch-punch melee ON. Press F (or LMB) for fist combos. '
                'Punch counter ticks on connect; soft-lock orbit mid-combo + '
                'hit flash. Soft-targets demo hostiles (and street suits).'
            )
        return 'Stretch-punch melee OFF.'

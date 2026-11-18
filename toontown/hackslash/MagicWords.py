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
        'orbit/pull for readability without hard-locking), brief hitstop/freeze '
        'on connect, impact squash/stretch juice + cream/ink fleck sparkles '
        'on connect (and when a corrupt smacks you), a '
        'brief white flash, Shift/X dodge roll with i-frames + rubber-hose '
        'afterimage trail and cream/ink i-frame pulse (ink sparkle / star pop '
        'when those i-frames eat a CorruptToon telegraph), soft-lock cream/ink '
        'reticle hose pop + brief FOV punch on '
        'acquire/snap, and an on-screen punch counter that ticks on hits then '
        'fades when the string breaks (finisher also cream-slam-flashes + '
        'FOV-punches). '
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
                'Stretch-punch melee ON. Press F (or LMB) for fist combos; '
                'Shift/X to dodge with a smear trail + cream/ink i-frame pulse '
                '(ink sparkle on perfect dodge). Connects squash/stretch; '
                'punch counter + soft-lock '
                'reticle pop / FOV punch / orbit + hit flash (cream slam flash '
                'on finisher). Soft-targets demo hostiles (and street suits).'
            )
        return 'Stretch-punch melee OFF.'

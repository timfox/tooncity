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
        '+ cream spark aftershock + soft cream wash pulse on connect (and when '
        'a corrupt smacks you), a '
        'brief white flash, Shift/X dodge roll with i-frames + rubber-hose '
        'afterimage trail, cream sparkle flecks along the trail + delayed '
        'cream aftershock + soft cream wash pulse, and cream/ink '
        'i-frame pulse (ink sparkle / star pop + cream star aftershock + soft '
        'cream wash pulse when those i-frames eat a CorruptToon telegraph), '
        'soft-lock cream/ink '
        'reticle hose pop + cream pulse ring + brief FOV punch on '
        'acquire/snap, and an on-screen punch counter that ticks on hits with a '
        'rubber-hose pop + cream sparkle + delayed cream aftershock then fades '
        'when the string breaks '
        '(finisher also cream-slam-flashes + cream sparkle hang + delayed '
        'cream aftershock + soft cream wash pulse after the slam, then '
        'FOV-punches; mid/finisher air '
        'juggle hangs with cream sparkle at apex + delayed cream aftershock). '
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
                'Shift/X to dodge with a smear trail + cream sparkle flecks + '
                'cream aftershock + cream wash + cream/ink i-frame pulse '
                '(ink sparkle + cream star aftershock + cream wash on perfect '
                'dodge). '
                'Connects squash/stretch + cream flecks / spark aftershock + '
                'cream wash; '
                'punch counter cream sparkle + cream aftershock + soft-lock '
                'reticle pop / cream pulse ring / FOV punch / orbit + hit flash '
                '(cream slam flash + sparkle hang + cream aftershock + cream '
                'wash on finisher; cream sparkle + cream aftershock at '
                'air-juggle hang). Soft-targets '
                'demo hostiles (and street suits).'
            )
        return 'Stretch-punch melee OFF.'

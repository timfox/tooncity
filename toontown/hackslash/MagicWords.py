"""Rubber-hose melee magic words. Imported/registered from MagicWordIndex."""

from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.spellbook import MagicWordConfig


class ToggleHackSlash(MagicWord):
    aliases = ['hackslash', 'melee', 'rubberhose', 'fists', 'stretchpunch']
    desc = 'Toggle real-time rubber-hose Oswald stretch-punch melee.'
    advancedDesc = (
        'Enables rubber-hose melee: press F (or LMB) for a short 3-hit stretch '
        'punch combo with soft nearest-hostile targeting, Tab / ` to cycle '
        'the sticky soft-lock next/prev among nearby hostiles, a subtle '
        'camera/facing nudge toward the sticky lock (mid-combo soft '
        'orbit/pull for readability without hard-locking; subtle yaw/aim '
        'assist on connect against the soft-lock so combos stay glued), '
        'brief hitstop/freeze '
        'on connect, impact squash/stretch juice + cream/ink fleck sparkles '
        '+ cream spark aftershock + soft cream wash pulse + cream wash '
        'aftershock on connect (and when '
        'a corrupt smacks you), a '
        'brief white flash, Shift/X dodge roll with i-frames + rubber-hose '
        'afterimage trail, cream sparkle flecks along the trail + delayed '
        'cream aftershock + soft cream wash pulse, and cream/ink '
        'i-frame pulse + soft i-frame cream wash pulse (late-dodge cancel '
        'window into stretch-punch; ink sparkle / star pop '
        '+ cream star aftershock + soft cream wash pulse + cream wash '
        'aftershock when those i-frames eat a CorruptToon telegraph, plus a '
        'short rewarded perfect-dodge counter window into a snappy bumped '
        'stretch-punch opener), '
        'soft-lock cream/ink '
        'reticle hose pop + cream pulse ring + soft cream wash pulse + brief '
        'FOV punch + soft FOV cream wash on '
        'acquire/snap (including manual Tab/` cycle snaps), and an on-screen '
        'punch counter that ticks on hits with a '
        'rubber-hose pop + cream sparkle + delayed cream aftershock + soft '
        'cream wash pulse + cream wash aftershock then fades when the string '
        'breaks '
        '(finisher also cream-slam-flashes + cream sparkle hang + delayed '
        'cream aftershock + soft cream wash pulse after the slam, then '
        'FOV-punches; mid/finisher air '
        'juggle hangs with cream sparkle at apex + delayed cream aftershock + '
        'soft cream wash pulse, and a mid-juggle cancel window into the '
        'finisher slam; when a corrupt smacks you, brief hurt stagger then a '
        'short recovery cancel into dodge or stretch-punch). '
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
                'Tab/` to cycle soft-lock next/prev; '
                'Shift/X to dodge with a smear trail + cream sparkle flecks + '
                'cream aftershock + cream wash + cream/ink i-frame pulse + '
                'i-frame cream wash, then F to cancel into a stretch-punch '
                '(ink sparkle + cream star aftershock + cream wash + cream '
                'wash aftershock on perfect dodge, then F again in the short '
                'counter window for a snappy bumped opener). '
                'Connects squash/stretch + cream flecks / spark aftershock + '
                'cream wash + cream wash aftershock; '
                'punch counter cream sparkle + cream aftershock + cream wash + '
                'cream wash aftershock + '
                'soft-lock reticle pop / cream pulse ring / cream wash / FOV '
                'punch / FOV cream wash / orbit + '
                'hit flash '
                '(cream slam flash + sparkle hang + cream aftershock + cream '
                'wash on finisher; cream sparkle + cream aftershock + cream '
                'wash at air-juggle hang, then F in the juggle cancel window '
                'for a finisher slam; after a smack, brief stagger then F or '
                'Shift in the recovery cancel). Soft-targets '
                'demo hostiles (and street suits).'
            )
        return 'Stretch-punch melee OFF.'

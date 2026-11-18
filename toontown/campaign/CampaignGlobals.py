"""Act table for the KH×Toontown multi-hood reclaim campaign."""

from toontown.toonbase import ToontownGlobals

# Pure HQ — story hub, lightly threatened but not a reclaim act.
HUB_ZONE = ToontownGlobals.ToontownCentral
HUB_NAME = 'Toontown Central'

# Per reclaim: multiplicative bump applied to HackSlashConfig.COMBO_DAMAGE.
POWER_BUMP_PER_RECLAIM = 0.08
POWER_BUMP_MAX = 0.40

# Escalating reclaim acts: explore → fight → reclaim → next hood.
# Finale uses a two-phase Ink Overlord fight.
ACTS = (
    {
        'id': 'loopy',
        'name': 'Loopy Lane',
        'zoneId': ToontownGlobals.LoopyLane,
        'seedPollution': 0.55,
        'packSize': 3,
        'maxPacks': 3,
        'corruptHp': 30,
        'corruptName': 'Ink Smudge',
        # Pure Smudge packs — Act 1 stays the familiar melee tutorial.
        'bruteFraction': 0.0,
        'banner': 'Act 1 — Corruption stains Loopy Lane!',
        'handoff': 'Loopy Lane is pure again! Next: Punchline Place (zone 2300).',
    },
    {
        'id': 'punchline',
        'name': 'Punchline Place',
        'zoneId': ToontownGlobals.PunchlinePlace,
        'seedPollution': 0.70,
        'packSize': 4,
        'maxPacks': 4,
        'corruptHp': 40,
        'corruptName': 'Gunk Gagster',
        # Mix in Sludge Brutes (tank + spit) with Gunk Gagster Smudges.
        'bruteFraction': 0.5,
        'bruteWaveStart': 1,
        'bruteName': 'Sludge Brute',
        'banner': 'Act 2 — Punchline Place is drowning in sludge!',
        'handoff': 'Punchline Place laughs clean! Finale awaits on Silly Street (zone 2100).',
    },
    {
        'id': 'finale',
        'name': 'Silly Street Finale',
        'zoneId': ToontownGlobals.SillyStreet,
        'seedPollution': 0.75,
        'packSize': 1,
        'maxPacks': 2,
        'corruptHp': 90,
        'corruptName': 'Ink Overlord',
        # Boss fight stays Overlord-only (no Brute mix).
        'bruteFraction': 0.0,
        'banner': 'Finale Phase 1 — The Ink Overlord rises on Silly Street!',
        'handoff': 'Toon City is saved! Purity restored across every neighborhood.',
        'finale': True,
        # Client-readable phase index (1-based) for reclaim director / telegraphs.
        'finalePhase': 1,
        # Phase 2 overrides after the first Silly Street reclaim clears.
        'phase2': {
            'seedPollution': 0.95,
            'packSize': 2,
            'maxPacks': 3,
            'corruptHp': 160,
            'corruptName': 'Ink Overlord Unleashed',
            'banner': 'Finale Phase 2 — Ink Overlord Unleashed! Finish it!',
            'finalePhase': 2,
            'transitionSting': True,
            'bruteFraction': 0.0,
        },
    },
)

# Client presentation for Silly Street Ink Overlord phases (1 / 2).
FINALE_PHASE_BANNER = {
    1: 'INK OVERLORD RISES',
    2: 'INK OVERLORD UNLEASHED',
}
FINALE_PHASE_SUB = {
    1: 'Magenta ink swell — read the wind-up!',
    2: 'Crimson ink fury — bigger telegraphs, hotter hits!',
}

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}
